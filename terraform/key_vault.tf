locals {
  # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault#certificate_permissions
  all_certificate_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "ManageContacts",
    "ManageIssuers",
    "GetIssuers",
    "ListIssuers",
    "SetIssuers",
    "DeleteIssuers",
  ]

  all_key_permissions = [
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

  all_secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
  ]
}

resource "azurerm_key_vault" "main" {
  name                     = "KV-CDT-PUB-CALITP-${local.env_letter}-001"
  location                 = data.azurerm_resource_group.main.location
  resource_group_name      = data.azurerm_resource_group.main.name
  sku_name                 = "standard"
  tenant_id                = data.azurerm_client_config.current.tenant_id
  purge_protection_enabled = true

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = var.ENGINEERING_GROUP_OBJECT_ID

    certificate_permissions = local.all_certificate_permissions
    key_permissions         = local.all_key_permissions
    secret_permissions      = local.all_secret_permissions
  }

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = var.DEVSECOPS_OBJECT_ID

    key_permissions    = local.all_key_permissions
    secret_permissions = local.all_secret_permissions
  }

  # https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references?tabs=azure-cli#granting-your-app-access-to-key-vault
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = azurerm_linux_web_app.main.identity.0.principal_id

    secret_permissions = ["Get"]
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags]
  }
}
