resource "azurerm_service_plan" "main" {
  name                = "ASP-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "P2v2"

  lifecycle {
    ignore_changes = [tags]
  }
}

# app_settings are managed manually through the portal since they contain secrets

resource "azurerm_linux_web_app" "main" {
  name                = "AS-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  service_plan_id     = azurerm_service_plan.main.id
  https_only          = true

  site_config {
    ftps_state             = "Disabled"
    vnet_route_all_enabled = true
    application_stack {
      docker_image     = "ghcr.io/cal-itp/benefits"
      docker_image_tag = local.env_name
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
      "DJANGO_LOAD_SAMPLE_DATA",
      "DJANGO_LOG_LEVEL",
      "DJANGO_MIGRATIONS_DIR",
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
    share_name   = azurerm_storage_container.config.name
    mount_path   = "/home/calitp/app/config"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [app_settings, tags]
  }
}

resource "azurerm_app_service_custom_hostname_binding" "main" {
  hostname            = local.hostname
  app_service_name    = azurerm_linux_web_app.main.name
  resource_group_name = data.azurerm_resource_group.main.name
}
