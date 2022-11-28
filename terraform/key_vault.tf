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
