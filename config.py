# --- GCP Configuration ---
GCP_PROJECT_ID = "your-gcp-project-id"
GCP_REGION = "us-central1"
GCP_ZONE = "us-central1-a"

# --- Legacy DB Configuration (for MCP Server) ---
# These are the names of the secrets in GCP Secret Manager
LEGACY_DB_HOST_SECRET = "legacy-db-host"
LEGACY_DB_USER_SECRET = "legacy-db-user"
LEGACY_DB_PASSWORD_SECRET = "legacy-db-password"
LEGACY_DB_NAME_SECRET = "legacy-db-name"

# --- Cloud SQL Configuration (for Terraform & Agents) ---
CLOUD_SQL_INSTANCE_NAME = "migrated-mysql-instance"
CLOUD_SQL_DB_VERSION = "MYSQL_8_0"
CLOUD_SQL_TIER = "db-n2-standard-2" # Adjust based on scale
CLOUD_SQL_ROOT_PASSWORD_SECRET = "cloud-sql-root-password"
CLOUD_SQL_BACKUP_START_TIME = "04:00"

# --- GCS Configuration ---
GCS_BUCKET_NAME_SUFFIX = "-migration-bucket"

# --- LLM and Agent Configuration ---
# Supported models: "openai/gpt-4o", "google/gemini-1.5-pro"
LLM_PROVIDER = "openai/gpt-4o"
OPENAI_API_KEY_SECRET = "openai-api-key" # Secret name in GCP Secret Manager
GEMINI_API_KEY_SECRET = "gemini-api-key" # Secret name in GCP Secret Manager

# --- Autogen Configuration ---
AUTOGEN_AGENT_TIMEOUT = 600 # Seconds
AUTOGEN_MAX_CONSECUTIVE_AUTO_REPLY = 15