resource "azurerm_storage_account" "main" {
  name                     = "sacdtcalitpp001"
  location                 = data.azurerm_resource_group.prod.location
  resource_group_name      = data.azurerm_resource_group.prod.name
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

resource "azurerm_storage_container" "config_dev" {
  name                  = "benefits-config-dev"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"

  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_storage_container" "config_test" {
  name                  = "benefits-config-test"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"

  lifecycle {
    prevent_destroy = true
  }
}

resource "azurerm_storage_container" "config_prod" {
  name                  = "benefits-config-prod"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"

  lifecycle {
    prevent_destroy = true
  }
}
