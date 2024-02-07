import logging
import os
import sys

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from django.conf import settings

logger = logging.getLogger(__name__)


KEY_VAULT_URL = "https://kv-cdt-pub-calitp-{env}-001.vault.azure.net/"


def get_secret_by_name(secret_name, client=None):
    """Read a value from the secret store, currently Azure KeyVault.

    When `settings.RUNTIME_ENVIRONMENT() == "local"`, reads from the environment instead.
    """

    runtime_env = settings.RUNTIME_ENVIRONMENT()

    if runtime_env == "local":
        logger.debug("Runtime environment is local, reading from environment instead of Azure KeyVault.")
        return os.environ.get(secret_name)

    elif client is None:
        # construct the KeyVault URL from the runtime environment
        # see https://docs.calitp.org/benefits/deployment/infrastructure/#environments
        # and https://github.com/cal-itp/benefits/blob/dev/terraform/key_vault.tf
        vault_url = KEY_VAULT_URL.format(env=runtime_env[0])
        logger.debug(f"Configuring Azure KeyVault secrets client for: {vault_url}")

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)

    secret = client.get_secret(secret_name)
    return secret.value


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 1:
        print("Provide the name of the secret to read")
        exit(1)

    secret_name = args[0]
    secret_value = get_secret_by_name(secret_name)

    print(f"[{settings.RUNTIME_ENVIRONMENT()}] {secret_name}: {secret_value}")
    exit(0)
