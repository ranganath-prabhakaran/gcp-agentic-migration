# gcp-agentic-migration/terraform/outputs.tf

output "orchestrator_vm_ip" {
  value = google_compute_instance.orchestrator_vm.network_interface.access_config.nat_ip
}

output "cloud_sql_instance_ip" {
  value = google_sql_database_instance.mysql_instance.private_ip_address
}

output "migration_bucket_name" {
  value = google_storage_bucket.migration_bucket.name
}

output "orchestrator_service_account_email" {
  value = google_service_account.migration_orchestrator_sa.email
}