# gcp-agentic-migration/terraform/main.tf

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.63.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}

# --- Service Account for GCE Orchestrator ---
resource "google_service_account" "migration_orchestrator_sa" {
  account_id   = "migration-orchestrator"
  display_name = "Service Account for Agentic Migration Orchestrator"
}

# --- IAM Bindings for the Service Account ---
resource "google_project_iam_member" "secret_accessor" {
  project = var.gcp_project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.migration_orchestrator_sa.email}"
}

resource "google_project_iam_member" "storage_admin" {
  project = var.gcp_project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.migration_orchestrator_sa.email}"
}

resource "google_project_iam_member" "cloud_sql_client" {
  project = var.gcp_project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.migration_orchestrator_sa.email}"
}

resource "google_project_iam_member" "compute_viewer" {
    project = var.gcp_project_id
    role    = "roles/compute.viewer"
    member  = "serviceAccount:${google_service_account.migration_orchestrator_sa.email}"
}

# --- VPC Network and Firewall Rules ---
resource "google_compute_network" "migration_vpc" {
  name                    = "migration-vpc"
  auto_create_subnetworks = true
}

resource "google_compute_firewall" "allow_ssh" {
  name    = "allow-ssh"
  network = google_compute_network.migration_vpc.name
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  source_ranges = ["0.0.0.0/0"]
}

# --- GCE Orchestrator Instance ---
resource "google_compute_instance" "orchestrator_vm" {
  name         = "migration-orchestrator-vm"
  machine_type = "e2-medium"
  zone         = var.gcp_zone
  tags         = ["ssh"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = google_compute_network.migration_vpc.id
    access_config {
      // Ephemeral IP
    }
  }

  service_account {
    email  = google_service_account.migration_orchestrator_sa.email
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update
    apt-get install -y python3-pip python3-venv git default-mysql-client
    # Install Mydumper/Myloader
    apt-get install -y mydumper
  EOT

  depends_on = [
    google_project_iam_member.secret_accessor,
    google_project_iam_member.storage_admin,
    google_project_iam_member.cloud_sql_client,
  ]
}

# --- Cloud Storage Bucket for Dumps ---
resource "google_storage_bucket" "migration_bucket" {
  name          = "${var.gcp_project_id}${var.gcs_bucket_name_suffix}"
  location      = var.gcp_region
  force_destroy = true

  lifecycle_rule {
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 30
    }
  }
  lifecycle_rule {
    action {
      type = "SetStorageClass"
      storage_class = "COLDLINE"
    }
    condition {
      age = 90
    }
  }
}

# --- Cloud SQL for MySQL Instance ---
data "google_secret_manager_secret_version" "cloud_sql_password" {
  project = var.gcp_project_id
  secret  = var.cloud_sql_root_password_secret
}

resource "google_sql_database_instance" "mysql_instance" {
  name             = var.cloud_sql_instance_name
  database_version = var.cloud_sql_db_version
  region           = var.gcp_region

  settings {
    tier = var.cloud_sql_tier
    ip_configuration {
      ipv4_enabled    = true
      private_network = google_compute_network.migration_vpc.id
    }
    backup_configuration {
      enabled            = true
      binary_log_enabled = true
      start_time         = var.cloud_sql_backup_start_time
    }
  }

  root_password = data.google_secret_manager_secret_version.cloud_sql_password.secret_data
  
  deletion_protection = false # Set to true for production
}