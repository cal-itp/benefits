# The pgAdmin Container App
resource "azurerm_container_app" "pgadmin" {
  name                         = "ca-cdt-pub-vip-calitp-${lower(var.env_letter)}-pgadmin"
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
    target_port                = 5050 # Since Azure blocks pgAdmin's default port (80)
    ip_security_restriction {
      action           = "Allow"
      ip_address_range = "127.0.0.1/32" # Dummy IP range to effectively block all traffic since we will manage access via Azure Portal
      name             = "DenyAllExceptPortal"
      description      = "Only allow traffic from manually added IP addresses via Azure Portal"
    }

    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  # Postgres admin password for psql access
  secret {
    name                = var.postgres_admin_password_secret_name
    identity            = "System"
    key_vault_secret_id = "${var.key_vault_secret_uri_prefix}/${var.postgres_admin_password_secret_name}"
  }

  # pgAdmin admin password for web login
  secret {
    name                = var.pgadmin_admin_password_secret_name
    identity            = "System"
    key_vault_secret_id = "${var.key_vault_secret_uri_prefix}/${var.pgadmin_admin_password_secret_name}"
  }

  template {
    min_replicas = 0
    max_replicas = 1

    cooldown_period_in_seconds = 3600 # Scale down to zero after 1 hour of inactivity

    volume {
      name         = azurerm_container_app_environment_storage.pgadmin.name
      storage_name = azurerm_container_app_environment_storage.pgadmin.name
      storage_type = "AzureFile"
    }

    container {
      name   = "pgadmin"
      image  = "dpage/pgadmin4:latest"
      cpu    = 0.5
      memory = "1Gi"

      # Mount the volume into the container's file system
      volume_mounts {
        name = azurerm_container_app_environment_storage.pgadmin.name
        path = local.pgadmin_storage_dir_path
      }

      # pgAdmin web UI
      env {
        name  = "PGADMIN_DEFAULT_EMAIL"
        value = "benefits-admin@calitp.org"
      }
      env {
        name        = "PGADMIN_DEFAULT_PASSWORD"
        secret_name = var.pgadmin_admin_password_secret_name
      }
      env {
        name  = "PGADMIN_CONFIG_SERVER_MODE" # Running on a web server requiring user authentication
        value = "True"
      }
      env {
        name  = "PGADMIN_LISTEN_PORT" # Override the default port that the server listens on
        value = "5050"
      }

      # psql default connection parameter values for convenience
      env {
        name  = "PGHOST"
        value = var.postgres_fqdn
      }
      env {
        name  = "PGUSER"
        value = var.postgres_admin_login
      }
      env {
        name  = "PGDATABASE"
        value = var.postgres_admin_db
      }
      env {
        name  = "PGSSLMODE"
        value = "verify-full"
      }
      env {
        name        = "PGPASSWORD"
        secret_name = var.postgres_admin_password_secret_name
      }
    }
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
