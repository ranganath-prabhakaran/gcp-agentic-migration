# gcp-agentic-migration/utils/gcp_secrets.py
from google.cloud import secretmanager
from.. import config

def get_secret(secret_id: str, version_id: str = "latest") -> str:
    """
    Retrieves a secret from Google Cloud Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{config.GCP_PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")