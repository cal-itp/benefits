resource "azurerm_key_vault" "main" {
  name                = "KV-CDT-PUB-CALITP-P-001"
  location            = data.azurerm_resource_group.prod.location
  resource_group_name = data.azurerm_resource_group.prod.name
  sku_name            = "standard"
  tenant_id           = data.azurerm_client_config.current.tenant_id

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags]
  }
}

# allow App Service to access the certificate
# https://learn.microsoft.com/en-us/azure/app-service/configure-ssl-certificate?tabs=apex%2Cportal#authorize-app-service-to-read-from-the-vault
resource "azurerm_key_vault_access_policy" "app_service_cert" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = "abfa0a7c-a6b6-4736-8310-5855508787cd"

  certificate_permissions = [
    "Get",
  ]
  secret_permissions = [
    "Get",
  ]
}

# allow the pipeline to access the certificate (below)
resource "azurerm_key_vault_access_policy" "prod_service_connection" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.PROD_SERVICE_CONNECTION_APP_ID

  certificate_permissions = [
    "Get",
  ]
}

data "azurerm_key_vault_certificate" "wildcard" {
  name         = "calitp-org-wildcard-cert"
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [
    azurerm_key_vault_access_policy.prod_service_connection
  ]
}
