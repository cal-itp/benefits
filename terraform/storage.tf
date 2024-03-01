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

resource "azurerm_recovery_services_vault" "main" {
  name                = "rsvcdtcalitp${lower(local.env_letter)}001"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  sku                 = "Standard"
  soft_delete_enabled = true

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_backup_container_storage_account" "main" {
  resource_group_name = data.azurerm_resource_group.main.name
  recovery_vault_name = azurerm_recovery_services_vault.main.name
  storage_account_id  = azurerm_storage_account.main.id
}

resource "azurerm_backup_policy_file_share" "policy" {
  name                = "${azurerm_storage_account.main.name}-backup-policy"
  resource_group_name = data.azurerm_resource_group.main.name
  recovery_vault_name = azurerm_recovery_services_vault.main.name
  timezone            = "UTC"

  backup {
    frequency = "Daily"
    time      = "14:00"
  }

  retention_daily {
    count = 1
  }

  retention_weekly {
    count    = 5
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
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
