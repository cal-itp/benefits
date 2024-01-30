import sys

from django.conf import settings

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


KEY_VAULT_URL = "https://kv-cdt-pub-calitp-{env}-001.vault.azure.net/"


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 1:
        print("Provide the name of the secret to read")
        exit(1)

    # construct the KeyVault URL from the runtime environment
    # see https://docs.calitp.org/benefits/deployment/infrastructure/#environments
    # and https://github.com/cal-itp/benefits/blob/dev/terraform/key_vault.tf
    runtime_env = settings.RUNTIME_ENVIRONMENT()
    vault_url = KEY_VAULT_URL.format(env=runtime_env[0])

    secret_name = args[0]

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    secret = client.get_secret(secret_name)

    print(f"Reading {secret_name} from {vault_url}")
    print(f"Value: {secret.value}")
    exit(0)
