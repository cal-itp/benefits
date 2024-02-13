import logging
import os
import re
import sys

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from django.conf import settings
from django.core.validators import RegexValidator

logger = logging.getLogger(__name__)


KEY_VAULT_URL = "https://kv-cdt-pub-calitp-{env}-001.vault.azure.net/"


class SecretNameValidator(RegexValidator):
    """RegexValidator that validates a secret name.

    Azure KeyVault currently enforces the following rules:

    * The value must be between 1 and 127 characters long.
    * Secret names can only contain alphanumeric characters and dashes.

    Read more about Azure KeyVault naming rules:
    https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/resource-name-rules#microsoftkeyvault

    Read more about Django validators:
    https://docs.djangoproject.com/en/5.0/ref/validators/#module-django.core.validators
    """

    def __init__(self, *args, **kwargs):
        kwargs["regex"] = re.compile(r"^[-a-zA-Z0-9]{1,127}$", re.ASCII)
        kwargs["message"] = (
            "Enter a valid secret name of between 1-127 alphanumeric ASCII characters and the hyphen character only."
        )
        super().__init__(*args, **kwargs)


NAME_VALIDATOR = SecretNameValidator()


def get_secret_by_name(secret_name, client=None):
    """Read a value from the secret store, currently Azure KeyVault.

    When `settings.RUNTIME_ENVIRONMENT() == "local"`, reads from the environment instead.
    """
    NAME_VALIDATOR(secret_name)

    runtime_env = settings.RUNTIME_ENVIRONMENT()

    if runtime_env == "local":
        logger.debug("Runtime environment is local, reading from environment instead of Azure KeyVault.")
        # environment variable names cannot contain the hyphen character
        # assume the variable name is the same but with underscores instead
        env_secret_name = secret_name.replace("-", "_")
        secret_value = os.environ.get(env_secret_name)
        # we have to replace literal newlines here with the actual newline character
        # to support local environment variables values that span multiple lines (e.g. PEM keys/certs)
        # because the VS Code Python extension doesn't support multiline environment variables
        # https://code.visualstudio.com/docs/python/environments#_environment-variables
        return secret_value.replace("\\n", "\n")

    elif client is None:
        # construct the KeyVault URL from the runtime environment
        # see https://docs.calitp.org/benefits/deployment/infrastructure/#environments
        # and https://github.com/cal-itp/benefits/blob/dev/terraform/key_vault.tf
        vault_url = KEY_VAULT_URL.format(env=runtime_env[0])
        logger.debug(f"Configuring Azure KeyVault secrets client for: {vault_url}")

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)

    secret_value = None

    if client is not None:
        try:
            secret = client.get_secret(secret_name)
            secret_value = secret.value
        except ClientAuthenticationError:
            logger.error("Could not authenticate to Azure KeyVault")
    else:
        logger.error("Azure KeyVault SecretClient was not configured")

    return secret_value


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 1:
        print("Provide the name of the secret to read")
        exit(1)

    secret_name = args[0]
    secret_value = get_secret_by_name(secret_name)

    print(f"[{settings.RUNTIME_ENVIRONMENT()}] {secret_name}: {secret_value}")
    exit(0)
