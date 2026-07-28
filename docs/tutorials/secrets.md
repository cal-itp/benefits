# Setting secrets

Secret values used by the Benefits application (such as API keys, private keys, certificates, etc.) are stored in an Azure Key Vault for each environment.

To set a secret, you can use the [Azure portal](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-portal?source=recommendations) or the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/keyvault/secret?view=azure-cli-latest#az-keyvault-secret-set).

There are helper scripts under `terraform/secrets` which build up the Azure CLI command, given some inputs. The usage is as follows:

First, make sure you are set up for [local development](../explanation/infrastructure.md#making-changes) and that you are in the `terraform/secrets` directory.

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

To verify the value of a secret, you can use the helper script named `read.sh`.

```bash
./read.sh <environment_letter> <secret_name>
```

## Refreshing secrets

Container apps pick up new key vault values [within 30 minutes](https://learn.microsoft.com/en-us/azure/container-apps/manage-secrets?tabs=azure-portal#key-vault-secret-uri-and-secret-rotation) without intervention. You can trigger an immediate reevaluation by deploying a new revision or stopping and restarting the container app.
