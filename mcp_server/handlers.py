# gcp-agentic-migration/mcp_server/handlers.py

import subprocess
import json
import pymysql
import os
from..utils.gcp_secrets import get_secret
from.. import config

class MigrationToolHandlers:
    def __init__(self):
        # Load secrets at initialization
        try:
            self.legacy_db_host = get_secret(config.LEGACY_DB_HOST_SECRET)
            self.legacy_db_user = get_secret(config.LEGACY_DB_USER_SECRET)
            self.legacy_db_password = get_secret(config.LEGACY_DB_PASSWORD_SECRET)
            self.legacy_db_name = get_secret(config.LEGACY_DB_NAME_SECRET)
        except Exception as e:
            print(f"Error loading legacy DB secrets: {e}")
            # Handle cases where secrets might not be needed immediately
            self.legacy_db_host = None

    def _run_command(self, command, cwd=None):
        """Helper to run shell commands and return structured output."""
        try:
            process = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=cwd
            )
            return {
                "status": "success",
                "stdout": process.stdout,
                "stderr": process.stderr,
                "returncode": process.returncode,
            }
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "stdout": e.stdout,
                "stderr": e.stderr,
                "returncode": e.returncode,
            }

    # --- Resources ---
    async def get_source_db_size(self):
        """Estimates the size of the source database."""
        if not self.legacy_db_host:
            return {"error": "Legacy DB credentials not configured."}
        try:
            connection = pymysql.connect(host=self.legacy_db_host,
                                         user=self.legacy_db_user,
                                         password=self.legacy_db_password,
                                         database=self.legacy_db_name,
                                         cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                sql = """
                SELECT table_schema AS 'database_name', 
                SUM(data_length + index_length) / 1024 / 1024 / 1024 AS 'size_in_gb' 
                FROM information_schema.TABLES 
                WHERE table_schema = %s
                GROUP BY table_schema;
                """
                cursor.execute(sql, (self.legacy_db_name,))
                result = cursor.fetchone()
            connection.close()
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_source_schema(self, tables: list = None):
        """Gets CREATE TABLE statements from the source database."""
        if not self.legacy_db_host:
            return {"error": "Legacy DB credentials not configured."}
        
        schemas = {}
        try:
            connection = pymysql.connect(host=self.legacy_db_host,
                                         user=self.legacy_db_user,
                                         password=self.legacy_db_password,
                                         database=self.legacy_db_name,
                                         cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                if not tables:
                    cursor.execute("SHOW TABLES")
                    tables = [for row in cursor.fetchall()]

                for table in tables:
                    cursor.execute(f"SHOW CREATE TABLE `{table}`")
                    schemas[table] = cursor.fetchone()
            connection.close()
            return {"status": "success", "data": schemas}
        except Exception as e:
            return {"status": "error", "message": str(e)}
            
    async def get_gcp_project_state(self):
        """Gets the state of key GCP resources."""
        command = f"gcloud sql instances describe {config.CLOUD_SQL_INSTANCE_NAME} --project={config.GCP_PROJECT_ID} --format=json"
        return self._run_command(command)

    # --- Tools ---
    async def provision_infra(self):
        """Provisions GCP infrastructure using Terraform."""
        tf_dir = os.path.join(os.getcwd(), 'terraform')
        command = f"terraform -chdir={tf_dir} init && terraform -chdir={tf_dir} apply -auto-approve -var='gcp_project_id={config.GCP_PROJECT_ID}' -var='gcp_region={config.GCP_REGION}' -var='gcp_zone={config.GCP_ZONE}' -var='cloud_sql_instance_name={config.CLOUD_SQL_INSTANCE_NAME}' -var='cloud_sql_db_version={config.CLOUD_SQL_DB_VERSION}' -var='cloud_sql_tier={config.CLOUD_SQL_TIER}' -var='cloud_sql_root_password_secret={config.CLOUD_SQL_ROOT_PASSWORD_SECRET}' -var='cloud_sql_backup_start_time={config.CLOUD_SQL_BACKUP_START_TIME}' -var='gcs_bucket_name_suffix={config.GCS_BUCKET_NAME_SUFFIX}'"
        return self._run_command(command)

    async def destroy_infra(self):
        """Destroys GCP infrastructure using Terraform."""
        tf_dir = os.path.join(os.getcwd(), 'terraform')
        command = f"terraform -chdir={tf_dir} destroy -auto-approve -var='gcp_project_id={config.GCP_PROJECT_ID}' -var='gcp_region={config.GCP_REGION}'"
        return self._run_command(command)

    async def run_gcs_import(self, bucket_uri: str, database: str):
        """Runs a Cloud SQL import from a GCS bucket."""
        command = f"gcloud sql import sql {config.CLOUD_SQL_INSTANCE_NAME} {bucket_uri} --database={database} --project={config.GCP_PROJECT_ID} --quiet"
        return self._run_command(command)

    async def run_dms_job(self, job_id: str):
        """Starts a Database Migration Service job."""
        command = f"gcloud database-migration jobs start {job_id} --region={config.GCP_REGION} --project={config.GCP_PROJECT_ID}"
        return self._run_command(command)

    async def run_mydumper(self, output_dir: str, threads: int = 4):
        """Runs the mydumper command."""
        command = f"mydumper --host={self.legacy_db_host} --user={self.legacy_db_user} --password='{self.legacy_db_password}' --database={self.legacy_db_name} --outputdir={output_dir} --threads={threads} --compress --long-query-guard=60"
        return self._run_command(command)

    async def run_myloader(self, input_dir: str, threads: int = 4):
        """Runs the myloader command."""
        cloud_sql_password = get_secret(config.CLOUD_SQL_ROOT_PASSWORD_SECRET)
        result = self._run_command(f"gcloud sql instances describe {config.CLOUD_SQL_INSTANCE_NAME} --project={config.GCP_PROJECT_ID} --format='json(ipAddresses.ipAddress)'")
        if result['status'] == 'error':
            return result
        cloud_sql_ip = json.loads(result['stdout'])['ipAddresses']['ipAddress']
        
        command = f"myloader --host={cloud_sql_ip} --user=root --password='{cloud_sql_password}' --database={self.legacy_db_name} --directory={input_dir} --threads={threads} --compress-protocol --verbose=3"
        return self._run_command(command)

    async def run_validation_script(self, script_content: str, language: str):
        """Runs a validation script."""
        if language == "sql":
            return {"status": "error", "message": "SQL validation script execution needs more implementation details for connecting to both databases."}
        elif language == "python":
            with open("temp_validation_script.py", "w") as f:
                f.write(script_content)
            result = self._run_command("python3 temp_validation_script.py")
            os.remove("temp_validation_script.py")
            return result
        else:
            return {"status": "error", "message": f"Unsupported language: {language}"}

    # --- Prompts ---
    async def get_gcp_encryption_recommendation(self):
        """Returns GCP's best practice encryption standards."""
        recommendation = {
            "status": "success",
            "data": {
                "title": "GCP Recommended Encryption Standards for Cloud SQL",
                "data_at_rest": "GCP encrypts customer data stored at rest by default, without any action required from you. Cloud SQL uses the AES-256 encryption algorithm. For additional control, you can use Customer-Managed Encryption Keys (CMEK).",
                "data_in_transit": "For connections to a Cloud SQL instance, you can enforce SSL/TLS encryption. It is best practice to configure all application clients to use SSL/TLS.",
                "recommendation": "Go with the GCP default encryption at rest and enforce SSL/TLS for all client connections for data in transit."
            }
        }
        return recommendation