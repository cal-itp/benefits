resource "azurerm_key_vault" "main" {
  name                = "KV-CDT-PUB-CALITP-P-001"
  location            = data.azurerm_resource_group.benefits.location
  resource_group_name = data.azurerm_resource_group.benefits.name
  sku_name            = "standard"
  tenant_id           = data.azurerm_client_config.current.tenant_id

  lifecycle {
    ignore_changes = [tags]
  }
}
