# The Benefits Container App
resource "azurerm_container_app" "benefits" {
  name                         = "ca-cdt-pub-vip-calitp-${lower(var.env_letter)}-001"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = var.resource_group_name
  revision_mode                = "Single"
  workload_profile_name        = "Consumption"

  identity {
    type = "SystemAssigned"
  }

  ingress {
    allow_insecure_connections = false
    external_enabled           = true
    target_port                = 8000

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  dynamic "secret" {
    # Only include secrets where 'exists' is true
    for_each = { for k, v in local.app_config_secrets : k => v if v.exists }
    content {
      name                = secret.key
      identity            = "System"
      key_vault_secret_id = "${var.key_vault_secret_uri_prefix}/${secret.key}"
    }
  }

  template {
    # Define the volume using the environment storage
    volume {
      name         = azurerm_container_app_environment_storage.main.name
      storage_name = azurerm_container_app_environment_storage.main.name
      storage_type = "AzureFile"
    }

    container {
      name   = "benefits"
      image  = "${var.container_registry}/${var.container_repository}:${var.container_tag}"
      cpu    = 0.5
      memory = "1Gi"

      # Mount the volume into the container's file system
      volume_mounts {
        name = azurerm_container_app_environment_storage.main.name
        path = local.django_storage_dir_path
      }

      # Set environment variables referencing secret config values
      dynamic "env" {
        for_each = { for k, v in local.app_config_secrets : k => v if v.exists }
        content {
          name        = env.value.env_name
          secret_name = env.key
        }
      }

      # Set environment variables referencing non-secret config values
      dynamic "env" {
        for_each = local.app_config
        content {
          name  = env.key
          value = env.value
        }
      }
    }
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }

  depends_on = [
    azurerm_container_app_environment_storage.main
  ]
}
