- [Create the corresponding secret in the Azure Key Vault](../../../tutorials/secrets/) for the environment
- Be sure to refresh the secrets for this to take effect!
  1. In the Azure portal, go to the App Service.
  1. Inside the App Service, navigate to Settings -> Environment variables.
  1. Click the **Pull reference values** button to force the App Service to bypass the 24-hour cache and fetch the latest values for Key Vault references. This triggers a graceful restart of the app.
