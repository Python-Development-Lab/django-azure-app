import os
import logging
from azure.keyvault.secrets import SecretClient
from azure.identity import ManagedIdentityCredential, DefaultAzureCredential

logger = logging.getLogger(__name__)
VAULT_URL = "https://django-app-kv.vault.azure.net/"
SECRET_MAP = {
    "SECRET_KEY": "DJANGO-SECRET-KEY",
    "AZURE_CLIENT_ID": "AZURE-CLIENT-ID",
    "AZURE_CLIENT_SECRET": "AZURE-CLIENT-SECRET",
    "AZURE_TENANT_ID": "AZURE-TENANT-ID",
    "DB_HOST": "DB-HOST",
    "DB_NAME": "DB-NAME",
    "DB_USER": "DB-USER",
    "DB_PASSWORD": "DB-PASSWORD",
    "APPINSIGHTS_CONNECTION_STRING": "APPINSIGHTS-CONNECTION-STRING",
}


def get_secret_client():
    try:
        credential = ManagedIdentityCredential()
        client = SecretClient(vault_url=VAULT_URL, credential=credential)
        client.get_secret("DJANGO-SECRET-KEY")
        logger.info("Key Vault: using ManagedIdentityCredential")
        return client
    except Exception:
        logger.info("Key Vault: falling back to DefaultAzureCredential")
        credential = DefaultAzureCredential()
        return SecretClient(vault_url=VAULT_URL, credential=credential)


def load_secrets_to_env():
    try:
        client = get_secret_client()
        for env_key, secret_name in SECRET_MAP.items():
            if not os.environ.get(env_key):
                value = client.get_secret(secret_name).value
                os.environ[env_key] = value
                logger.info(f"Key Vault: loaded {env_key}")
    except Exception as e:
        logger.warning(f"Key Vault: failed - {e}")
