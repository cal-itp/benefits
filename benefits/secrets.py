import sys
import os

# When this script is run directly, its directory ('/calitp/app/benefits') is
# added to the start of sys.path. This causes Python to import the local
# `benefits/locale` package instead of the standard library `locale` module,
# which breaks `argparse` and other modules.
#
# The fix is to temporarily remove the script's directory from the path,
# import the standard library `locale` to get it into Python's module cache,
# and then restore the path so that other local imports work correctly.
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir in sys.path:
    # Temporarily remove the script's directory from the path
    sys.path.remove(script_dir)
    # Import and cache the standard library `locale`
    import locale  # noqa: F401

    # Restore the original path
    sys.path.insert(0, script_dir)
else:
    # If the script's directory wasn't on the path, no conflict exists.
    import locale  # noqa: F401

import argparse  # noqa: E402
import logging  # noqa: E402
import re  # noqa: E402

from azure.core.exceptions import ClientAuthenticationError  # noqa: E402
from azure.identity import DefaultAzureCredential  # noqa: E402
from azure.keyvault.certificates import CertificateClient  # noqa: E402
from azure.keyvault.secrets import SecretClient  # noqa: E402
from django.conf import settings  # noqa: E402
from django.core.validators import RegexValidator  # noqa: E402

logger = logging.getLogger(__name__)


KEY_VAULT_URL = "https://kv-cdt-pub-calitp-{env}-001.vault.azure.net/"


def _get_value_by_name(name, client_cls, get_value_func, client=None):
    """Read a value (secret, cert) from the store, currently Azure KeyVault.

    When `settings.RUNTIME_ENVIRONMENT() == "local"`, reads from the environment instead.
    """
    runtime_env = settings.RUNTIME_ENVIRONMENT()

    if runtime_env == "local":
        logger.debug("Runtime environment is local, reading from environment instead of Azure KeyVault.")
        # environment variable names cannot contain the hyphen character
        # assume the variable name is the same but with underscores instead
        env_var_name = name.replace("-", "_")
        value = os.environ.get(env_var_name)
        # we have to replace literal newlines here with the actual newline character
        # to support local environment variables values that span multiple lines (e.g. PEM keys/certs)
        # because the VS Code Python extension doesn't support multiline environment variables
        # https://code.visualstudio.com/docs/python/environments#_environment-variables
        return value.replace("\\n", "\n")

    elif client is None:
        # construct the KeyVault URL from the runtime environment
        # see https://docs.calitp.org/benefits/deployment/infrastructure/#environments
        # and https://github.com/cal-itp/benefits/blob/main/terraform/key_vault.tf
        vault_url = KEY_VAULT_URL.format(env=runtime_env[0])
        logger.debug(f"Configuring Azure KeyVault client: {client_cls.__name__} for vault: {vault_url}")

        credential = DefaultAzureCredential()
        client = client_cls(vault_url=vault_url, credential=credential)

    value = None

    if client is not None:
        try:
            value = get_value_func(client, name)
        except ClientAuthenticationError:
            logger.error("Could not authenticate to Azure KeyVault")
    else:
        logger.error(f"Azure KeyVault client was not configured: {client_cls.__name__}")

    return value


def get_cert_by_name(cert_name, client: CertificateClient = None):
    """Read a certificate from the store, currently Azure KeyVault.

    When `settings.RUNTIME_ENVIRONMENT() == "local"`, reads from the environment instead.
    """

    def _get_value(_client: CertificateClient, _name: str):
        try:
            cert = _client.get_certificate(_name)
            return cert.cer
        except ClientAuthenticationError:
            logger.error("Could not authenticate to Azure KeyVault")
        return None

    return _get_value_by_name(cert_name, CertificateClient, _get_value, client)


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


def get_secret_by_name(secret_name, client: SecretClient = None):
    """Read a value from the secret store, currently Azure KeyVault.

    When `settings.RUNTIME_ENVIRONMENT() == "local"`, reads from the environment instead.
    """
    NAME_VALIDATOR(secret_name)

    def _get_value(_client: SecretClient, _name: str):
        try:
            secret = _client.get_secret(_name)
            return secret.value
        except ClientAuthenticationError:
            logger.error("Could not authenticate to Azure KeyVault")
        return None

    return _get_value_by_name(secret_name, SecretClient, _get_value, client)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="secrets")
    parser.add_argument("-s", "--secret", help="The name of a secret to read")
    parser.add_argument("-c", "--cert", help="The name of a certificate to read")

    args = parser.parse_args()

    if args.secret:
        secret_value = get_secret_by_name(args.secret)
        print(f"[{settings.RUNTIME_ENVIRONMENT()} secret] {args.secret}: {secret_value}")
    if args.cert:
        cert_value = get_cert_by_name(args.cert)
        print(f"[{settings.RUNTIME_ENVIRONMENT()} cert] {args.cert}:")
        print(cert_value)

    if not (args.secret or args.cert):
        parser.print_help()

    exit(0)
