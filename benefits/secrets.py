import sys

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Provide the Key Vault URL and the name of the secret to read")
        exit(1)

    vault_url = args[0]
    secret_name = args[1]

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    secret = client.get_secret(secret_name)

    print(f"Reading {secret_name} from {vault_url}")
    print(f"Value: {secret.value}")
    exit(0)
