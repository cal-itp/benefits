locals {
  django_storage_dir_path = "/calitp/app/data"
  app_config_secrets = {
    # Amplitude
    "analytics-key" = { env_name = "ANALYTICS_KEY", exists = !local.is_dev }, # Only create env var in non-dev environments
    # Django Azure Email Backend
    (local.azure_communication_connection_string_name) = { env_name = "AZURE_COMMUNICATION_CONNECTION_STRING", exists = true },
    # Django settings
    "django-allowed-hosts"                 = { env_name = "DJANGO_ALLOWED_HOSTS", exists = true },
    "django-debug"                         = { env_name = "DJANGO_DEBUG", exists = !local.is_prod }, # Only create secret in non-prod environments
    "django-log-level"                     = { env_name = "DJANGO_LOG_LEVEL", exists = true },
    "django-recaptcha-secret-key"          = { env_name = "DJANGO_RECAPTCHA_SECRET_KEY", exists = true },
    "django-recaptcha-site-key"            = { env_name = "DJANGO_RECAPTCHA_SITE_KEY", exists = true },
    "django-secret-key"                    = { env_name = "DJANGO_SECRET_KEY", exists = true },
    "django-trusted-origins"               = { env_name = "DJANGO_TRUSTED_ORIGINS", exists = true },
    "django-db-name"                       = { env_name = "DJANGO_DB_NAME", exists = true },
    "django-db-user"                       = { env_name = "DJANGO_DB_USER", exists = true },
    (local.django_db_password_secret_name) = { env_name = "DJANGO_DB_PASSWORD", exists = true },
    # Postgres settings
    "use-postgres"                              = { env_name = "USE_POSTGRES", exists = true },
    (local.postgres_admin_password_secret_name) = { env_name = "POSTGRES_PASSWORD", exists = true },
    "healthcheck-user-agents"                   = { env_name = "HEALTHCHECK_USER_AGENTS", exists = !local.is_dev }, # Only create secret in non-dev environments
    # Google SSO for Admin
    "google-sso-client-id"         = { env_name = "GOOGLE_SSO_CLIENT_ID", exists = true },
    "google-sso-project-id"        = { env_name = "GOOGLE_SSO_PROJECT_ID", exists = true },
    "google-sso-client-secret"     = { env_name = "GOOGLE_SSO_CLIENT_SECRET", exists = true },
    "google-sso-allowable-domains" = { env_name = "GOOGLE_SSO_ALLOWABLE_DOMAINS", exists = true },
    "google-sso-staff-list"        = { env_name = "GOOGLE_SSO_STAFF_LIST", exists = true },
    "google-sso-superuser-list"    = { env_name = "GOOGLE_SSO_SUPERUSER_LIST", exists = true },
    "sso-show-form-on-admin-page"  = { env_name = "SSO_SHOW_FORM_ON_ADMIN_PAGE", exists = true },
    # Sentry
    "sentry-dsn"                = { env_name = "SENTRY_DSN", exists = true },
    "sentry-report-uri"         = { env_name = "SENTRY_REPORT_URI", exists = true },
    "sentry-traces-sample-rate" = { env_name = "SENTRY_TRACES_SAMPLE_RATE", exists = true }
  }
  app_config = {
    # Requests
    "REQUESTS_CONNECT_TIMEOUT" = "5",
    "REQUESTS_READ_TIMEOUT"    = "20",
    # Django Azure Email Backend
    "DEFAULT_FROM_EMAIL" = local.sender_email,
    # Django settings
    "DJANGO_STORAGE_DIR" = local.django_storage_dir_path,
    # Database settings
    "POSTGRES_HOSTNAME" = azurerm_postgresql_flexible_server.main.fqdn,
    "POSTGRES_DB"       = local.postgres_admin_db,
    "POSTGRES_USER"     = local.postgres_admin_login,
    # Sentry
    "SENTRY_ENVIRONMENT" = local.env_name
  }
}
# The Container App Environment
resource "azurerm_container_app_environment" "main" {
  name                           = "CAE-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
  location                       = data.azurerm_resource_group.main.location
  resource_group_name            = data.azurerm_resource_group.main.name
  log_analytics_workspace_id     = azurerm_log_analytics_workspace.main.id
  infrastructure_subnet_id       = azurerm_subnet.main["ACAPP"].id
  internal_load_balancer_enabled = false

  # Set the Environment type to Workload profile
  # Set the Plan type to Consumption
  workload_profile {
    name                  = "Consumption"
    workload_profile_type = "Consumption"
    minimum_count         = 0
    maximum_count         = 0
  }

  # Azure manages infrastructure_resource_group_name and may change it
  # Changes force new resource creation, so we ignore it to prevent replacing the environment on every apply
  lifecycle {
    ignore_changes = [tags, infrastructure_resource_group_name]
  }
}

# The Container App
resource "azurerm_container_app" "main" {
  name                         = "ca-cdt-pub-vip-calitp-${lower(local.env_letter)}-001"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = data.azurerm_resource_group.main.name
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
      key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/${secret.key}"
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
      image  = "${var.CONTAINER_REGISTRY}/${var.CONTAINER_REPOSITORY}:${var.CONTAINER_TAG}"
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

# Manages the 'benefits-storage' file share of the Container App Environment
resource "azurerm_container_app_environment_storage" "main" {
  name                         = "benefits-storage"
  container_app_environment_id = azurerm_container_app_environment.main.id
  account_name                 = azurerm_storage_account.main.name
  access_key                   = azurerm_storage_account.main.primary_access_key
  share_name                   = azurerm_storage_share.main.name
  access_mode                  = "ReadWrite"
}
