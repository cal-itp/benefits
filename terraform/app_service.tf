resource "azurerm_service_plan" "main" {
  name                = "ASP-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  os_type             = "Linux"
  sku_name            = "B1"

  lifecycle {
    ignore_changes = [tags]
  }
}

locals {
  data_mount = "/home/calitp/app/data"
}

resource "azurerm_linux_web_app" "main" {
  name                      = "AS-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
  location                  = data.azurerm_resource_group.main.location
  resource_group_name       = data.azurerm_resource_group.main.name
  service_plan_id           = azurerm_service_plan.main.id
  https_only                = true
  virtual_network_subnet_id = local.subnet_id

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

  app_settings = {
    # app setting used solely for refreshing secrets - see https://github.com/MicrosoftDocs/azure-docs/issues/79855#issuecomment-1265664801
    "change_me_to_refresh_secrets" = "change me in the portal to refresh all secrets",

    "DOCKER_ENABLE_CI"                    = "true",
    "DOCKER_REGISTRY_SERVER_URL"          = "https://ghcr.io/",
    "WEBSITE_HTTPLOGGING_RETENTION_DAYS"  = "99999",
    "WEBSITE_TIME_ZONE"                   = "America/Los_Angeles",
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false",
    "WEBSITES_PORT"                       = "8000",

    "ANALYTICS_KEY" = local.is_dev ? null : "${local.secret_prefix}analytics-key)",

    # Requests
    "REQUESTS_CONNECT_TIMEOUT" = "${local.secret_prefix}requests-connect-timeout)",
    "REQUESTS_READ_TIMEOUT"    = "${local.secret_prefix}requests-read-timeout)",

    # Django settings
    "DJANGO_ALLOWED_HOSTS" = "${local.secret_prefix}django-allowed-hosts)",
    "DJANGO_DB_DIR"        = "${local.secret_prefix}django-db-dir)",
    "DJANGO_DEBUG"         = local.is_prod ? null : "${local.secret_prefix}django-debug)",
    "DJANGO_LOG_LEVEL"     = "${local.secret_prefix}django-log-level)",

    "DJANGO_RECAPTCHA_SECRET_KEY" = local.is_dev ? null : "${local.secret_prefix}django-recaptcha-secret-key)",
    "DJANGO_RECAPTCHA_SITE_KEY"   = local.is_dev ? null : "${local.secret_prefix}django-recaptcha-site-key)",

    "DJANGO_SECRET_KEY"      = "${local.secret_prefix}django-secret-key)",
    "DJANGO_TRUSTED_ORIGINS" = "${local.secret_prefix}django-trusted-origins)",

    "HEALTHCHECK_USER_AGENTS" = local.is_dev ? null : "${local.secret_prefix}healthcheck-user-agents)",

    # Google SSO for Admin

    "GOOGLE_SSO_CLIENT_ID"         = "${local.secret_prefix}google-sso-client-id)",
    "GOOGLE_SSO_PROJECT_ID"        = "${local.secret_prefix}google-sso-project-id)",
    "GOOGLE_SSO_CLIENT_SECRET"     = "${local.secret_prefix}google-sso-client-secret)",
    "GOOGLE_SSO_ALLOWABLE_DOMAINS" = "${local.secret_prefix}google-sso-allowable-domains)",
    "GOOGLE_SSO_STAFF_LIST"        = "${local.secret_prefix}google-sso-staff-list)",
    "GOOGLE_SSO_SUPERUSER_LIST"    = "${local.secret_prefix}google-sso-superuser-list)"

    # Sentry
    "SENTRY_DSN"                = "${local.secret_prefix}sentry-dsn)",
    "SENTRY_ENVIRONMENT"        = local.env_name,
    "SENTRY_REPORT_URI"         = "${local.secret_prefix}sentry-report-uri)",
    "SENTRY_TRACES_SAMPLE_RATE" = "${local.secret_prefix}sentry-traces-sample-rate)",
  }

  storage_account {
    access_key   = azurerm_storage_account.main.primary_access_key
    account_name = azurerm_storage_account.main.name
    name         = "benefits-data"
    type         = "AzureFiles"
    share_name   = azurerm_storage_share.data.name
    mount_path   = local.data_mount
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags]
  }
}

resource "azurerm_app_service_custom_hostname_binding" "main" {
  hostname            = local.hostname
  app_service_name    = azurerm_linux_web_app.main.name
  resource_group_name = data.azurerm_resource_group.main.name
}

# migrations

moved {
  from = azurerm_app_service_custom_hostname_binding.prod
  to   = azurerm_app_service_custom_hostname_binding.main
}
