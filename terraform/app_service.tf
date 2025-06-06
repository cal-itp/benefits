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
  data_mount = "/calitp/app/data"
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
    "DOCKER_REGISTRY_SERVER_URL"          = "https://ghcr.io/"
    "WEBSITE_TIME_ZONE"                   = "America/Los_Angeles",
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "true",
    "WEBSITES_PORT"                       = "8000",

    "ANALYTICS_KEY" = local.is_dev ? null : "${local.secret_prefix}analytics-key)",

    # Requests
    "REQUESTS_CONNECT_TIMEOUT" = "${local.secret_prefix}requests-connect-timeout)",
    "REQUESTS_READ_TIMEOUT"    = "${local.secret_prefix}requests-read-timeout)",

    # Django settings
    "DJANGO_ALLOWED_HOSTS" = "${local.secret_prefix}django-allowed-hosts)",
    "DJANGO_STORAGE_DIR"   = "${local.secret_prefix}django-storage-dir)",
    "DJANGO_DEBUG"         = local.is_prod ? null : "${local.secret_prefix}django-debug)",
    "DJANGO_LOG_LEVEL"     = "${local.secret_prefix}django-log-level)",
    "DJANGO_RECAPTCHA_SECRET_KEY" = "${local.secret_prefix}django-recaptcha-secret-key)",
    "DJANGO_RECAPTCHA_SITE_KEY"   = "${local.secret_prefix}django-recaptcha-site-key)",
    "DJANGO_SECRET_KEY"      = "${local.secret_prefix}django-secret-key)",
    "DJANGO_TRUSTED_ORIGINS" = "${local.secret_prefix}django-trusted-origins)",

    "HEALTHCHECK_USER_AGENTS" = local.is_dev ? null : "${local.secret_prefix}healthcheck-user-agents)",

    # Transit payment processor settings
    "LITTLEPAY_ADDITIONAL_CARDTYPES" = "${local.secret_prefix}littlepay-additional-cardtypes)",
    "LITTLEPAY_QA_API_BASE_URL" = "${local.secret_prefix}littlepay-qa-api-base-url"
    "LITTLEPAY_PROD_API_BASE_URL" = "${local.secret_prefix}littlepay-prod-api-base-url"

    "SWITCHIO_QA_API_BASE_URL" = "${local.secret_prefix}switchio-qa-api-base-url"
    "SWITCHIO_PROD_API_BASE_URL" = "${local.secret_prefix}switchio-prod-api-base-url"

    # Google SSO for Admin

    "GOOGLE_SSO_CLIENT_ID"         = "${local.secret_prefix}google-sso-client-id)",
    "GOOGLE_SSO_PROJECT_ID"        = "${local.secret_prefix}google-sso-project-id)",
    "GOOGLE_SSO_CLIENT_SECRET"     = "${local.secret_prefix}google-sso-client-secret)",
    "GOOGLE_SSO_ALLOWABLE_DOMAINS" = "${local.secret_prefix}google-sso-allowable-domains)",
    "GOOGLE_SSO_STAFF_LIST"        = "${local.secret_prefix}google-sso-staff-list)",
    "GOOGLE_SSO_SUPERUSER_LIST"    = "${local.secret_prefix}google-sso-superuser-list)",
    "SSO_SHOW_FORM_ON_ADMIN_PAGE"  = "${local.secret_prefix}sso-show-form-on-admin-page)"

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
