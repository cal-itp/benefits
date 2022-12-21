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

# app_settings are managed manually through the portal since they contain secrets

## PROD ##

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
    application_stack {
      docker_image     = "ghcr.io/cal-itp/benefits"
      docker_image_tag = "prod"
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

  # Confusingly named argument; these are settings / environment variables that should be unique to each slot. Also known as "deployment slot settings".
  # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_web_app#app_setting_names
  # https://docs.microsoft.com/en-us/azure/app-service/deploy-staging-slots#which-settings-are-swapped
  sticky_settings {
    # sort them so that they don't change when we rearrange them
    app_setting_names = sort([
      # custom config
      "ANALYTICS_KEY",
      "DJANGO_ALLOWED_HOSTS",
      "DJANGO_DEBUG",
      "DJANGO_LOAD_SAMPLE_DATA",
      "DJANGO_LOG_LEVEL",
      "DJANGO_MIGRATIONS_DIR",
      "DJANGO_RATE_LIMIT",
      "DJANGO_RATE_LIMIT_METHODS",
      "DJANGO_RATE_LIMIT_PERIOD",
      "DJANGO_RECAPTCHA_SECRET_KEY",
      "DJANGO_RECAPTCHA_SITE_KEY",
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
    ])
  }

  storage_account {
    access_key   = azurerm_storage_account.main.primary_access_key
    account_name = azurerm_storage_account.main.name
    name         = "benefits-config"
    type         = "AzureBlob"
    share_name   = azurerm_storage_container.config_prod.name
    mount_path   = "/home/calitp/app/config"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [app_settings, tags]
  }
}

resource "azurerm_app_service_custom_hostname_binding" "prod" {
  hostname            = "benefits.calitp.org"
  app_service_name    = azurerm_linux_web_app.main.name
  resource_group_name = data.azurerm_resource_group.prod.name

  # Ignore ssl_state and thumbprint as they are managed externally
  lifecycle {
    ignore_changes = [ssl_state, thumbprint]
  }
}

## DEV ##

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
    prevent_destroy = true
    ignore_changes  = [app_settings, tags]
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

## TEST ##

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
    prevent_destroy = true
    ignore_changes  = [app_settings, tags]
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

# migrations

moved {
  from = azurerm_app_service_custom_hostname_binding.main
  to   = azurerm_app_service_custom_hostname_binding.prod
}
