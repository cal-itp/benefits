locals {
  django_storage_dir_path = "/calitp/app/data"
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
  name                         = "CA-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
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

      # Amplitude
      env {
        name  = "ANALYTICS_KEY"
        value = local.is_dev ? null : "${local.secret_prefix}analytics-key)"
      }

      # Requests
      env {
        name  = "REQUESTS_CONNECT_TIMEOUT"
        value = "${local.secret_prefix}requests-connect-timeout)"
      }
      env {
        name  = "REQUESTS_READ_TIMEOUT"
        value = "${local.secret_prefix}requests-read-timeout)"
      }

      # Django Azure Email Backend
      env {
        name  = "AZURE_COMMUNICATION_CONNECTION_STRING"
        value = "${local.secret_prefix}${local.azure_communication_connection_string_name})"
      }
      env {
        name  = "DEFAULT_FROM_EMAIL"
        value = local.sender_email
      }

      # Django settings
      env {
        name  = "DJANGO_ALLOWED_HOSTS"
        value = "${local.secret_prefix}django-allowed-hosts)"
      }
      env {
        name  = "DJANGO_STORAGE_DIR"
        value = local.django_storage_dir_path
      }
      env {
        name  = "DJANGO_DEBUG"
        value = local.is_prod ? null : "${local.secret_prefix}django-debug)"
      }
      env {
        name  = "DJANGO_LOG_LEVEL"
        value = "${local.secret_prefix}django-log-level)"
      }
      env {
        name  = "DJANGO_RECAPTCHA_SECRET_KEY"
        value = "${local.secret_prefix}django-recaptcha-secret-key)"
      }
      env {
        name  = "DJANGO_RECAPTCHA_SITE_KEY"
        value = "${local.secret_prefix}django-recaptcha-site-key)"
      }
      env {
        name  = "DJANGO_SECRET_KEY"
        value = "${local.secret_prefix}django-secret-key)"
      }
      env {
        name  = "DJANGO_TRUSTED_ORIGINS"
        value = "${local.secret_prefix}django-trusted-origins)"
      }
      env {
        name  = "DJANGO_DB_NAME"
        value = "${local.secret_prefix}django-db-name)"
      }
      env {
        name  = "DJANGO_DB_USER"
        value = "${local.secret_prefix}django-db-user)"
      }
      env {
        name  = "DJANGO_DB_PASSWORD"
        value = "${local.secret_prefix}${local.django_db_password_secret_name})"
      }

      # Database settings
      env {
        name  = "USE_POSTGRES"
        value = "${local.secret_prefix}use-postgres)"
      }
      env {
        name  = "POSTGRES_HOSTNAME"
        value = azurerm_postgresql_flexible_server.main.fqdn
      }
      env {
        name  = "HEALTHCHECK_USER_AGENTS"
        value = local.is_dev ? null : "${local.secret_prefix}healthcheck-user-agents)"
      }

      # Google SSO for Admin
      env {
        name  = "GOOGLE_SSO_CLIENT_ID"
        value = "${local.secret_prefix}google-sso-client-id)"
      }
      env {
        name  = "GOOGLE_SSO_PROJECT_ID"
        value = "${local.secret_prefix}google-sso-project-id)"
      }
      env {
        name  = "GOOGLE_SSO_CLIENT_SECRET"
        value = "${local.secret_prefix}google-sso-client-secret)"
      }
      env {
        name  = "GOOGLE_SSO_ALLOWABLE_DOMAINS"
        value = "${local.secret_prefix}google-sso-allowable-domains)"
      }
      env {
        name  = "GOOGLE_SSO_STAFF_LIST"
        value = "${local.secret_prefix}google-sso-staff-list)"
      }
      env {
        name  = "GOOGLE_SSO_SUPERUSER_LIST"
        value = "${local.secret_prefix}google-sso-superuser-list)"
      }
      env {
        name  = "SSO_SHOW_FORM_ON_ADMIN_PAGE"
        value = "${local.secret_prefix}sso-show-form-on-admin-page)"
      }

      # Sentry
      env {
        name  = "SENTRY_DSN"
        value = "${local.secret_prefix}sentry-dsn)"
      }
      env {
        name  = "SENTRY_ENVIRONMENT"
        value = local.env_name
      }
      env {
        name  = "SENTRY_REPORT_URI"
        value = "${local.secret_prefix}sentry-report-uri)"
      }
      env {
        name  = "SENTRY_TRACES_SAMPLE_RATE"
        value = "${local.secret_prefix}sentry-traces-sample-rate)"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
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
