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

resource "azurerm_key_vault_access_policy" "devsecops" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.DEVSECOPS_OBJECT_ID

  # allow the pipeline to access the certificate (below)
  certificate_permissions = [
    "Get",
  ]
  key_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "GetRotationPolicy",
    "SetRotationPolicy",
    "Rotate",
  ]
  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
  ]
}

data "azurerm_key_vault_certificate" "wildcard" {
  name         = "calitp-org-wildcard-cert"
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [
    azurerm_key_vault_access_policy.devsecops
  ]
}

# migrations

moved {
  from = azurerm_key_vault_access_policy.prod_service_connection
  to   = azurerm_key_vault_access_policy.devsecops
}
