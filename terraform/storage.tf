resource "azurerm_storage_account" "main" {
  name                     = "sacdtcalitp${lower(local.env_letter)}001"
  location                 = data.azurerm_resource_group.main.location
  resource_group_name      = data.azurerm_resource_group.main.name
  account_tier             = "Standard"
  account_replication_type = "RAGRS"

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

resource "azurerm_storage_share" "data" {
  name                 = "benefits-data"
  storage_account_name = azurerm_storage_account.main.name
  quota                = 5
  enabled_protocol     = "SMB"
  acl {
    id = "benefits-data-rwdl"
    access_policy {
      permissions = "rwdl"
    }
  }
}
