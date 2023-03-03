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

## Refreshing secrets

To make sure the Benefits application uses the latest secret values in Key Vault, you will need to make a change to the app service's configuration. If you don't do this step, the application will instead use cached values, which may not be what you expect. See the [Azure docs](https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references?tabs=azure-cli#rotation) for more details.

The steps are:

1. After setting new secret values, go to the App Service configuration in Azure Portal, and change the value of the setting named `change_me_to_refresh_secrets`.
1. Save your changes.

The effects of following those steps should be:

- A restart of the App Service is triggered.
- The next time that our Azure infrastructure pipeline is run, the value of `change_me_to_refresh_secrets` is set back to the value defined in our Terraform file for the App Service resource.
