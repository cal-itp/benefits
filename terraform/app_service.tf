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

  app_settings = sensitive(data.dotenv.main.env)

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
    ignore_changes  = [tags]
  }
}
