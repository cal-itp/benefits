resource "azurerm_service_plan" "main" {
  name                = "ASP-CDT-PUB-VIP-CALITP-P-001"
  location            = data.azurerm_resource_group.prod.location
  resource_group_name = data.azurerm_resource_group.prod.name
  os_type             = "Linux"
  sku_name            = "P2v2"

  lifecycle {
    ignore_changes = [tags]
  }
}

# app_settings and storage_account are managed manually through the portal since they contain secrets

resource "azurerm_linux_web_app" "main" {
  name                = "AS-CDT-PUB-VIP-CALITP-P-001"
  location            = data.azurerm_resource_group.prod.location
  resource_group_name = data.azurerm_resource_group.prod.name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = true

  site_config {
    ftps_state = "Disabled"
  }

  identity {
    identity_ids = []
    type         = "SystemAssigned"
  }

  logs {
    detailed_error_messages = false
    failed_request_tracing  = false

    http_logs {
      file_system {
        retention_in_days = 99999
        retention_in_mb   = 100
      }
    }
  }

  sticky_settings {
    # Confusingly named argument; these are settings / environment variables that should be unique to each slot. Also known as "deployment slot settings".
    # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_web_app#app_setting_names
    # https://docs.microsoft.com/en-us/azure/app-service/deploy-staging-slots#which-settings-are-swapped
    app_setting_names = [
      "ANALYTICS_KEY",
      "APPLICATIONINSIGHTS_CONNECTION_STRING",
      "DJANGO_ALLOWED_HOSTS",
      "DJANGO_INIT_PATH",
      "DJANGO_LOG_LEVEL",
      "DJANGO_TRUSTED_ORIGINS",
    ]
  }

  lifecycle {
    ignore_changes = [app_settings, tags]
  }
}

resource "azurerm_linux_web_app_slot" "dev" {
  name           = "dev"
  https_only     = true
  app_service_id = azurerm_linux_web_app.main.id

  site_config {
    ftps_state             = "Disabled"
    vnet_route_all_enabled = true
  }

  identity {
    identity_ids = []
    type         = "SystemAssigned"
  }

  logs {
    detailed_error_messages = false
    failed_request_tracing  = false

    http_logs {
      file_system {
        retention_in_days = 99999
        retention_in_mb   = 100
      }
    }
  }

  lifecycle {
    ignore_changes = [app_settings, storage_account, tags]
  }
}

resource "azurerm_app_service_slot_custom_hostname_binding" "dev" {
  app_service_slot_id = azurerm_linux_web_app_slot.dev.id
  hostname            = "dev-benefits.calitp.org"
}

resource "azurerm_linux_web_app_slot" "test" {
  name           = "test"
  https_only     = true
  app_service_id = azurerm_linux_web_app.main.id

  site_config {
    ftps_state             = "Disabled"
    vnet_route_all_enabled = true
  }

  identity {
    identity_ids = []
    type         = "SystemAssigned"
  }

  logs {
    detailed_error_messages = false
    failed_request_tracing  = false

    http_logs {
      file_system {
        retention_in_days = 99999
        retention_in_mb   = 100
      }
    }
  }

  lifecycle {
    ignore_changes = [app_settings, storage_account, tags]
  }
}

resource "azurerm_app_service_slot_custom_hostname_binding" "test" {
  app_service_slot_id = azurerm_linux_web_app_slot.test.id
  hostname            = "test-benefits.calitp.org"
}
