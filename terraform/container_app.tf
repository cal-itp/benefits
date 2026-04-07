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
    for_each = local.is_dev ? [] : [1] # Only create secret in non-dev environments
    content {
      name                = "analytics-key"
      identity            = "System"
      key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/analytics-key"
    }
  }

  secret {
    name                = local.azure_communication_connection_string_name
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/${local.azure_communication_connection_string_name}"
  }

  secret {
    name                = "django-allowed-hosts"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/django-allowed-hosts"
  }

  dynamic "secret" {
    for_each = local.is_prod ? [] : [1] # Only create secret in non-prod environments
    content {
      name                = "django-debug"
      identity            = "System"
      key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/django-debug"
    }
  }

  secret {
    name                = "django-log-level"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/django-log-level"
  }

  secret {
    name                = "django-recaptcha-secret-key"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/django-recaptcha-secret-key"
  }

  secret {
    name                = "django-recaptcha-site-key"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/django-recaptcha-site-key"
  }

  secret {
    name                = "django-secret-key"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/django-secret-key"
  }

  secret {
    name                = "django-trusted-origins"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/django-trusted-origins"
  }

  secret {
    name                = "django-db-name"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/django-db-name"
  }

  secret {
    name                = "django-db-user"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/django-db-user"
  }

  secret {
    name                = local.django_db_password_secret_name
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/${local.django_db_password_secret_name}"
  }

  secret {
    name                = "use-postgres"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/use-postgres"
  }

  secret {
    name                = local.postgres_admin_password_secret_name
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/${local.postgres_admin_password_secret_name}"
  }

  dynamic "secret" {
    for_each = local.is_dev ? [] : [1] # Only create secret in non-dev environments
    content {
      name                = "healthcheck-user-agents"
      identity            = "System"
      key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/healthcheck-user-agents"
    }
  }

  secret {
    name                = "google-sso-client-id"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/google-sso-client-id"
  }

  secret {
    name                = "google-sso-project-id"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/google-sso-project-id"
  }

  secret {
    name                = "google-sso-client-secret"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/google-sso-client-secret"
  }

  secret {
    name                = "google-sso-allowable-domains"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/google-sso-allowable-domains"
  }

  secret {
    name                = "google-sso-staff-list"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/google-sso-staff-list"
  }

  secret {
    name                = "google-sso-superuser-list"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/google-sso-superuser-list"
  }

  secret {
    name                = "sso-show-form-on-admin-page"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/sso-show-form-on-admin-page"
  }

  secret {
    name                = "sentry-dsn"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/sentry-dsn"
  }

  secret {
    name                = "sentry-report-uri"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/sentry-report-uri"
  }

  secret {
    name                = "sentry-traces-sample-rate"
    identity            = "System"
    key_vault_secret_id = "${local.key_vault_secret_uri_prefix}/sentry-traces-sample-rate"
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
      dynamic "env" {
        for_each = local.is_dev ? [] : [1] # Only create env var in non-dev environments
        content {
          name        = "ANALYTICS_KEY"
          secret_name = "analytics-key"
        }
      }

      # Requests
      env {
        name  = "REQUESTS_CONNECT_TIMEOUT"
        value = "5"
      }
      env {
        name  = "REQUESTS_READ_TIMEOUT"
        value = "20"
      }

      # Django Azure Email Backend
      env {
        name        = "AZURE_COMMUNICATION_CONNECTION_STRING"
        secret_name = local.azure_communication_connection_string_name
      }
      env {
        name  = "DEFAULT_FROM_EMAIL"
        value = local.sender_email
      }

      # Django settings
      env {
        name        = "DJANGO_ALLOWED_HOSTS"
        secret_name = "django-allowed-hosts"
      }
      env {
        name  = "DJANGO_STORAGE_DIR"
        value = local.django_storage_dir_path
      }
      dynamic "env" {
        for_each = local.is_prod ? [] : [1] # Only create secret in non-prod environments
        content {
          name        = "DJANGO_DEBUG"
          secret_name = "django-debug"
        }
      }
      env {
        name        = "DJANGO_LOG_LEVEL"
        secret_name = "django-log-level"
      }
      env {
        name        = "DJANGO_RECAPTCHA_SECRET_KEY"
        secret_name = "django-recaptcha-secret-key"
      }
      env {
        name        = "DJANGO_RECAPTCHA_SITE_KEY"
        secret_name = "django-recaptcha-site-key"
      }
      env {
        name        = "DJANGO_SECRET_KEY"
        secret_name = "django-secret-key"
      }
      env {
        name        = "DJANGO_TRUSTED_ORIGINS"
        secret_name = "django-trusted-origins"
      }
      env {
        name        = "DJANGO_DB_NAME"
        secret_name = "django-db-name"
      }
      env {
        name        = "DJANGO_DB_USER"
        secret_name = "django-db-user"
      }
      env {
        name        = "DJANGO_DB_PASSWORD"
        secret_name = local.django_db_password_secret_name
      }

      # Database settings
      env {
        name        = "USE_POSTGRES"
        secret_name = "use-postgres"
      }
      env {
        name  = "POSTGRES_HOSTNAME"
        value = azurerm_postgresql_flexible_server.main.fqdn
      }
      env {
        name  = "POSTGRES_DB"
        value = local.postgres_admin_db
      }
      env {
        name  = "POSTGRES_USER"
        value = local.postgres_admin_login
      }
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = local.postgres_admin_password_secret_name
      }
      dynamic "env" {
        for_each = local.is_dev ? [] : [1] # Only create secret in non-dev environments
        content {
          name        = "HEALTHCHECK_USER_AGENTS"
          secret_name = "healthcheck-user-agents"
        }
      }
      # Google SSO for Admin
      env {
        name        = "GOOGLE_SSO_CLIENT_ID"
        secret_name = "google-sso-client-id"
      }
      env {
        name        = "GOOGLE_SSO_PROJECT_ID"
        secret_name = "google-sso-project-id"
      }
      env {
        name        = "GOOGLE_SSO_CLIENT_SECRET"
        secret_name = "google-sso-client-secret"
      }
      env {
        name        = "GOOGLE_SSO_ALLOWABLE_DOMAINS"
        secret_name = "google-sso-allowable-domains"
      }
      env {
        name        = "GOOGLE_SSO_STAFF_LIST"
        secret_name = "google-sso-staff-list"
      }
      env {
        name        = "GOOGLE_SSO_SUPERUSER_LIST"
        secret_name = "google-sso-superuser-list"
      }
      env {
        name        = "SSO_SHOW_FORM_ON_ADMIN_PAGE"
        secret_name = "sso-show-form-on-admin-page"
      }

      # Sentry
      env {
        name        = "SENTRY_DSN"
        secret_name = "sentry-dsn"
      }
      env {
        name  = "SENTRY_ENVIRONMENT"
        value = local.env_name
      }
      env {
        name        = "SENTRY_REPORT_URI"
        secret_name = "sentry-report-uri"
      }
      env {
        name        = "SENTRY_TRACES_SAMPLE_RATE"
        secret_name = "sentry-traces-sample-rate"
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
