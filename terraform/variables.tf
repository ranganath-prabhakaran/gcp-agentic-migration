# gcp-agentic-migration/terraform/variables.tf

variable "gcp_project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "gcp_region" {
  description = "The GCP region for resources."
  type        = string
}

variable "gcp_zone" {
  description = "The GCP zone for resources."
  type        = string
}

variable "cloud_sql_instance_name" {
  description = "Name of the Cloud SQL instance."
  type        = string
}

variable "cloud_sql_db_version" {
  description = "MySQL version for Cloud SQL."
  type        = string
}

variable "cloud_sql_tier" {
  description = "Machine type for Cloud SQL."
  type        = string
}

variable "cloud_sql_root_password_secret" {
  description = "The name of the secret in Secret Manager for the Cloud SQL root password."
  type        = string
}

variable "cloud_sql_backup_start_time" {
  description = "The start time for daily backups (HH:MM)."
  type        = string
}

variable "gcs_bucket_name_suffix" {
  description = "Suffix for the GCS migration bucket name."
  type        = string
}