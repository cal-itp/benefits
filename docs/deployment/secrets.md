# Setting secrets

Secret values used by the Benefits application (such as API keys, private keys, certificates, etc.) are stored in an Azure Key Vault for each environment.

To set a secret, you can use the [Azure portal](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-portal?source=recommendations) or the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/keyvault/secret?view=azure-cli-latest#az-keyvault-secret-set).

There are helper scripts under `terraform/secrets` which build up the Azure CLI command, given some inputs. The usage is as follows:

First, make sure you are set up for [local development](../infrastructure/#local-development) and that you are in the `terraform/secrets` directory.

```bash
cd terraform/secrets
```

To set a secret by providing a value:

```bash
./value.sh <environment_letter> <secret_name> <secret_value>
```

where `environment_letter` is `D` for development, `T` for test, and `P` for production.

To set a secret by providing the path of a file containing the secret (useful for [multi-line secrets](https://learn.microsoft.com/en-us/azure/key-vault/secrets/multiline-secrets)):

```bash
./file.sh <environment_letter> <secret_name> <file_path>
```
