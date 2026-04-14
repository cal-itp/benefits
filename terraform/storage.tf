resource "azurerm_storage_account" "main" {
  name                             = "sacdtcalitp${lower(local.env_letter)}001"
  location                         = data.azurerm_resource_group.main.location
  resource_group_name              = data.azurerm_resource_group.main.name
  account_tier                     = "Standard"
  account_replication_type         = "RAGRS"
  allow_nested_items_to_be_public  = false
  cross_tenant_replication_enabled = false

  blob_properties {
    last_access_time_enabled = true
    versioning_enabled       = true

    container_delete_retention_policy {
      days = 7
    }

    delete_retention_policy {
      days = 7
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }
}

# The File Share for the Django storage directory
resource "azurerm_storage_share" "web" {
  name               = "web-storage"
  storage_account_id = azurerm_storage_account.main.id
  quota              = 10 # Max size in GB
}

# The File Share for the pgAdmin storage directory
resource "azurerm_storage_share" "pgadmin" {
  name               = "pgadmin-storage"
  storage_account_id = azurerm_storage_account.main.id
  quota              = 10 # Max size in GB
}
