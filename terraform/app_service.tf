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

# app_settings and storage_account are managed manually through the portal since they contain secrets. Issue to move the latter in:
# https://github.com/cal-itp/benefits/issues/686

resource "azurerm_linux_web_app" "main" {
  name                      = "AS-CDT-PUB-VIP-CALITP-P-001"
  location                  = data.azurerm_resource_group.prod.location
  resource_group_name       = data.azurerm_resource_group.prod.name
  service_plan_id           = azurerm_service_plan.main.id
  https_only                = true
  virtual_network_subnet_id = data.azurerm_subnet.main.id

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

  # Confusingly named argument; these are settings / environment variables that should be unique to each slot. Also known as "deployment slot settings".
  # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_web_app#app_setting_names
  # https://docs.microsoft.com/en-us/azure/app-service/deploy-staging-slots#which-settings-are-swapped
  sticky_settings {
    app_setting_names = [
      # custom config
      "ANALYTICS_KEY",
      "DJANGO_ALLOWED_HOSTS",
      "DJANGO_LOG_LEVEL",
      "DJANGO_TRUSTED_ORIGINS",

      # populated through auto-instrumentation
      # https://docs.microsoft.com/en-us/azure/azure-monitor/app/azure-web-apps#enable-application-insights
      "APPINSIGHTS_INSTRUMENTATIONKEY",
      "APPINSIGHTS_PROFILERFEATURE_VERSION",
      "APPINSIGHTS_SNAPSHOTFEATURE_VERSION",
      "APPLICATIONINSIGHTS_CONFIGURATION_CONTENT",
      "APPLICATIONINSIGHTS_CONNECTION_STRING",
      "ApplicationInsightsAgent_EXTENSION_VERSION",
      "DiagnosticServices_EXTENSION_VERSION",
      "InstrumentationEngine_EXTENSION_VERSION",
      "SnapshotDebugger_EXTENSION_VERSION",
      "XDT_MicrosoftApplicationInsights_BaseExtensions",
      "XDT_MicrosoftApplicationInsights_Mode",
      "XDT_MicrosoftApplicationInsights_NodeJS",
      "XDT_MicrosoftApplicationInsights_PreemptSdk",
      "XDT_MicrosoftApplicationInsightsJava",
    ]
  }

  lifecycle {
    ignore_changes = [app_settings, storage_account, tags]
  }
}

resource "azurerm_linux_web_app_slot" "dev" {
  name                      = "dev"
  https_only                = true
  app_service_id            = azurerm_linux_web_app.main.id
  virtual_network_subnet_id = data.azurerm_subnet.main.id

  site_config {
    ftps_state             = "Disabled"
    vnet_route_all_enabled = true
    application_stack {
      docker_image     = "ghcr.io/cal-itp/benefits"
      docker_image_tag = "dev"
    }
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
    ignore_changes = [app_settings, tags]
  }

  # setup files
  storage_account {
    access_key   = azurerm_storage_account.main.primary_access_key
    account_name = azurerm_storage_account.main.name
    # use the same name
    name       = azurerm_storage_container.config_dev.name
    type       = "AzureBlob"
    share_name = azurerm_storage_container.config_dev.name
    mount_path = "/home/calitp/app/config"
  }
}

resource "azurerm_app_service_slot_custom_hostname_binding" "dev" {
  app_service_slot_id = azurerm_linux_web_app_slot.dev.id
  hostname            = "dev-benefits.calitp.org"
}

resource "azurerm_linux_web_app_slot" "test" {
  name                      = "test"
  https_only                = true
  app_service_id            = azurerm_linux_web_app.main.id
  virtual_network_subnet_id = data.azurerm_subnet.main.id

  site_config {
    ftps_state             = "Disabled"
    vnet_route_all_enabled = true
    application_stack {
      docker_image     = "ghcr.io/cal-itp/benefits"
      docker_image_tag = "test"
    }
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
    ignore_changes = [app_settings, tags]
  }

  # setup files
  storage_account {
    access_key   = azurerm_storage_account.main.primary_access_key
    account_name = azurerm_storage_account.main.name
    # use the same name
    name       = azurerm_storage_container.config_test.name
    type       = "AzureBlob"
    share_name = azurerm_storage_container.config_test.name
    mount_path = "/home/calitp/app/config"
  }
}

resource "azurerm_app_service_slot_custom_hostname_binding" "test" {
  app_service_slot_id = azurerm_linux_web_app_slot.test.id
  hostname            = "test-benefits.calitp.org"
}
