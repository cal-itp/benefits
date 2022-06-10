resource "azurerm_storage_account" "main" {
  name                     = "sacdtcalitpp001"
  location                 = data.azurerm_resource_group.prod.location
  resource_group_name      = data.azurerm_resource_group.prod.name
  account_tier             = "Standard"
  account_replication_type = "RAGRS"

  lifecycle {
    ignore_changes = [tags]
  }
}
