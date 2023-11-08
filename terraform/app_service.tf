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
    "DJANGO_ADMIN"         = (local.is_prod || local.is_test) ? null : "${local.secret_prefix}django-admin)",
    "DJANGO_ALLOWED_HOSTS" = "${local.secret_prefix}django-allowed-hosts)",
    "DJANGO_DB_DIR"        = "${local.secret_prefix}django-db-dir)",
    "DJANGO_DB_RESET"      = "${local.secret_prefix}django-db-reset)",
    "DJANGO_DEBUG"         = local.is_prod ? null : "${local.secret_prefix}django-debug)",
    "DJANGO_LOG_LEVEL"     = "${local.secret_prefix}django-log-level)",

    "DJANGO_RECAPTCHA_SECRET_KEY" = local.is_dev ? null : "${local.secret_prefix}django-recaptcha-secret-key)",
    "DJANGO_RECAPTCHA_SITE_KEY"   = local.is_dev ? null : "${local.secret_prefix}django-recaptcha-site-key)",

    "DJANGO_SECRET_KEY"      = "${local.secret_prefix}django-secret-key)",
    "DJANGO_TRUSTED_ORIGINS" = "${local.secret_prefix}django-trusted-origins)",

    "HEALTHCHECK_USER_AGENTS" = local.is_dev ? null : "${local.secret_prefix}healthcheck-user-agents)",

    # Sentry
    "SENTRY_DSN"                = "${local.secret_prefix}sentry-dsn)",
    "SENTRY_ENVIRONMENT"        = local.env_name,
    "SENTRY_REPORT_URI"         = "${local.secret_prefix}sentry-report-uri)",
    "SENTRY_TRACES_SAMPLE_RATE" = "${local.secret_prefix}sentry-traces-sample-rate)",

    # Environment variables for data migration
    "MST_SENIOR_GROUP_ID"                                  = "${local.secret_prefix}mst-senior-group-id)",
    "MST_VETERAN_GROUP_ID"                                 = "${local.secret_prefix}mst-veteran-group-id)",
    "MST_COURTESY_CARD_GROUP_ID"                           = "${local.secret_prefix}mst-courtesy-card-group-id)"
    "SACRT_SENIOR_GROUP_ID"                                = "${local.secret_prefix}sacrt-senior-group-id)"
    "SBMTD_SENIOR_GROUP_ID"                                = "${local.secret_prefix}sbmtd-senior-group-id)",
    "SBMTD_MOBILITY_PASS_GROUP_ID"                         = "${local.secret_prefix}sbmtd-mobility-pass-group-id)"
    "CLIENT_PRIVATE_KEY"                                   = "${local.secret_prefix}client-private-key)"
    "CLIENT_PUBLIC_KEY"                                    = "${local.secret_prefix}client-public-key)"
    "MST_SERVER_PUBLIC_KEY_URL"                            = "${local.secret_prefix}mst-server-public-key-url)"
    "SBMTD_SERVER_PUBLIC_KEY_URL"                          = "${local.secret_prefix}sbmtd-server-public-key-url)"
    "MST_PAYMENT_PROCESSOR_CLIENT_CERT"                    = "${local.secret_prefix}mst-payment-processor-client-cert)"
    "MST_PAYMENT_PROCESSOR_CLIENT_CERT_PRIVATE_KEY"        = "${local.secret_prefix}mst-payment-processor-client-cert-private-key)"
    "MST_PAYMENT_PROCESSOR_CLIENT_CERT_ROOT_CA"            = "${local.secret_prefix}mst-payment-processor-client-cert-root-ca)"
    "SACRT_PAYMENT_PROCESSOR_CLIENT_CERT"                  = "${local.secret_prefix}sacrt-payment-processor-client-cert)"
    "SACRT_PAYMENT_PROCESSOR_CLIENT_CERT_PRIVATE_KEY"      = "${local.secret_prefix}sacrt-payment-processor-client-cert-private-key)"
    "SACRT_PAYMENT_PROCESSOR_CLIENT_CERT_ROOT_CA"          = "${local.secret_prefix}sacrt-payment-processor-client-cert-root-ca)"
    "SBMTD_PAYMENT_PROCESSOR_CLIENT_CERT"                  = "${local.secret_prefix}sbmtd-payment-processor-client-cert)"
    "SBMTD_PAYMENT_PROCESSOR_CLIENT_CERT_PRIVATE_KEY"      = "${local.secret_prefix}sbmtd-payment-processor-client-cert-private-key)"
    "SBMTD_PAYMENT_PROCESSOR_CLIENT_CERT_ROOT_CA"          = "${local.secret_prefix}sbmtd-payment-processor-client-cert-root-ca)"
    "AUTH_PROVIDER_CLIENT_ID"                              = "${local.secret_prefix}auth-provider-client-id)"
    "AUTH_PROVIDER_AUTHORITY"                              = "${local.secret_prefix}auth-provider-authority)"
    "SENIOR_AUTH_PROVIDER_CLIENT_NAME"                     = "${local.secret_prefix}senior-auth-provider-client-name)"
    "SENIOR_AUTH_PROVIDER_SCOPE"                           = "${local.secret_prefix}senior-auth-provider-scope)"
    "SENIOR_AUTH_PROVIDER_CLAIM"                           = "${local.secret_prefix}senior-auth-provider-claim)"
    "SENIOR_AUTH_PROVIDER_SCHEME"                          = "${local.secret_prefix}senior-auth-provider-scheme)"
    "VETERAN_AUTH_PROVIDER_CLIENT_NAME"                    = "${local.secret_prefix}veteran-auth-provider-client-name)"
    "VETERAN_AUTH_PROVIDER_SCOPE"                          = "${local.secret_prefix}veteran-auth-provider-scope)"
    "VETERAN_AUTH_PROVIDER_CLAIM"                          = "${local.secret_prefix}veteran-auth-provider-claim)"
    "VETERAN_AUTH_PROVIDER_SCHEME"                         = "${local.secret_prefix}veteran-auth-provider-scheme)"
    "MST_SENIOR_VERIFIER_NAME"                             = "${local.secret_prefix}mst-senior-verifier-name)"
    "MST_SENIOR_VERIFIER_ACTIVE"                           = "${local.secret_prefix}mst-senior-verifier-active)"
    "MST_VETERAN_VERIFIER_NAME"                            = "${local.secret_prefix}mst-veteran-verifier-name)"
    "MST_VETERAN_VERIFIER_ACTIVE"                          = "${local.secret_prefix}mst-veteran-verifier-active)"
    "COURTESY_CARD_VERIFIER_NAME"                          = "${local.secret_prefix}courtesy-card-verifier-name)"
    "COURTESY_CARD_VERIFIER_ACTIVE"                        = "${local.secret_prefix}courtesy-card-verifier-active)"
    "COURTESY_CARD_VERIFIER_API_URL"                       = "${local.secret_prefix}courtesy-card-verifier-api-url)"
    "COURTESY_CARD_VERIFIER_API_AUTH_HEADER"               = "${local.secret_prefix}courtesy-card-verifier-api-auth-header)"
    "COURTESY_CARD_VERIFIER_API_AUTH_KEY"                  = "${local.secret_prefix}courtesy-card-verifier-api-auth-key)"
    "COURTESY_CARD_VERIFIER_JWE_CEK_ENC"                   = "${local.secret_prefix}courtesy-card-verifier-jwe-cek-enc)"
    "COURTESY_CARD_VERIFIER_JWE_ENCRYPTION_ALG"            = "${local.secret_prefix}courtesy-card-verifier-jwe-encryption-alg)"
    "COURTESY_CARD_VERIFIER_JWS_SIGNING_ALG"               = "${local.secret_prefix}courtesy-card-verifier-jws-signing-alg)"
    "SACRT_SENIOR_VERIFIER_NAME"                           = "${local.secret_prefix}sacrt-senior-verifier-name)"
    "SACRT_SENIOR_VERIFIER_ACTIVE"                         = "${local.secret_prefix}sacrt-senior-verifier-active)"
    "SBMTD_SENIOR_VERIFIER_NAME"                           = "${local.secret_prefix}sbmtd-senior-verifier-name)"
    "SBMTD_SENIOR_VERIFIER_ACTIVE"                         = "${local.secret_prefix}sbmtd-senior-verifier-active)"
    "MST_PAYMENT_PROCESSOR_NAME"                           = "${local.secret_prefix}mst-payment-processor-name)"
    "MST_PAYMENT_PROCESSOR_API_BASE_URL"                   = "${local.secret_prefix}mst-payment-processor-api-base-url)"
    "MST_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_ENDPOINT"      = "${local.secret_prefix}mst-payment-processor-api-access-token-endpoint)"
    "MST_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_KEY"   = "${local.secret_prefix}mst-payment-processor-api-access-token-request-key)"
    "MST_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_VAL"   = "${local.secret_prefix}mst-payment-processor-api-access-token-request-val)"
    "MST_PAYMENT_PROCESSOR_CARD_TOKENIZE_URL"              = "${local.secret_prefix}mst-payment-processor-card-tokenize-url)"
    "MST_PAYMENT_PROCESSOR_CARD_TOKENIZE_FUNC"             = "${local.secret_prefix}mst-payment-processor-card-tokenize-func)"
    "MST_PAYMENT_PROCESSOR_CARD_TOKENIZE_ENV"              = "${local.secret_prefix}mst-payment-processor-card-tokenize-env)"
    "SACRT_PAYMENT_PROCESSOR_NAME"                         = "${local.secret_prefix}sacrt-payment-processor-name)"
    "SACRT_PAYMENT_PROCESSOR_API_BASE_URL"                 = "${local.secret_prefix}sacrt-payment-processor-api-base-url)"
    "SACRT_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_ENDPOINT"    = "${local.secret_prefix}sacrt-payment-processor-api-access-token-endpoint)"
    "SACRT_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_KEY" = "${local.secret_prefix}sacrt-payment-processor-api-access-token-request-key)"
    "SACRT_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_VAL" = "${local.secret_prefix}sacrt-payment-processor-api-access-token-request-val)"
    "SACRT_PAYMENT_PROCESSOR_CARD_TOKENIZE_URL"            = "${local.secret_prefix}sacrt-payment-processor-card-tokenize-url)"
    "SACRT_PAYMENT_PROCESSOR_CARD_TOKENIZE_FUNC"           = "${local.secret_prefix}sacrt-payment-processor-card-tokenize-func)"
    "SACRT_PAYMENT_PROCESSOR_CARD_TOKENIZE_ENV"            = "${local.secret_prefix}sacrt-payment-processor-card-tokenize-env)"
    "SBMTD_PAYMENT_PROCESSOR_NAME"                         = "${local.secret_prefix}sbmtd-payment-processor-name)"
    "SBMTD_PAYMENT_PROCESSOR_API_BASE_URL"                 = "${local.secret_prefix}sbmtd-payment-processor-api-base-url)"
    "SBMTD_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_ENDPOINT"    = "${local.secret_prefix}sbmtd-payment-processor-api-access-token-endpoint)"
    "SBMTD_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_KEY" = "${local.secret_prefix}sbmtd-payment-processor-api-access-token-request-key)"
    "SBMTD_PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_VAL" = "${local.secret_prefix}sbmtd-payment-processor-api-access-token-request-val)"
    "SBMTD_PAYMENT_PROCESSOR_CARD_TOKENIZE_URL"            = "${local.secret_prefix}sbmtd-payment-processor-card-tokenize-url)"
    "SBMTD_PAYMENT_PROCESSOR_CARD_TOKENIZE_FUNC"           = "${local.secret_prefix}sbmtd-payment-processor-card-tokenize-func)"
    "SBMTD_PAYMENT_PROCESSOR_CARD_TOKENIZE_ENV"            = "${local.secret_prefix}sbmtd-payment-processor-card-tokenize-env)"
    "MST_AGENCY_SHORT_NAME"                                = "${local.secret_prefix}mst-agency-short-name)"
    "MST_AGENCY_LONG_NAME"                                 = "${local.secret_prefix}mst-agency-long-name)"
    "MST_AGENCY_JWS_SIGNING_ALG"                           = "${local.secret_prefix}mst-agency-jws-signing-alg)"
    "SACRT_AGENCY_SHORT_NAME"                              = "${local.secret_prefix}sacrt-agency-short-name)"
    "SACRT_AGENCY_LONG_NAME"                               = "${local.secret_prefix}sacrt-agency-long-name)"
    "SACRT_AGENCY_MERCHANT_ID"                             = "${local.secret_prefix}sacrt-agency-merchant-id)"
    "SACRT_AGENCY_ACTIVE"                                  = "${local.secret_prefix}sacrt-agency-active)"
    "SACRT_AGENCY_JWS_SIGNING_ALG"                         = "${local.secret_prefix}sacrt-agency-jws-signing-alg)"
    "SBMTD_AGENCY_SHORT_NAME"                              = "${local.secret_prefix}sbmtd-agency-short-name)"
    "SBMTD_AGENCY_LONG_NAME"                               = "${local.secret_prefix}sbmtd-agency-long-name)"
    "SBMTD_AGENCY_MERCHANT_ID"                             = "${local.secret_prefix}sbmtd-agency-merchant-id)"
    "SBMTD_AGENCY_ACTIVE"                                  = "${local.secret_prefix}sbmtd-agency-active)"
    "SBMTD_AGENCY_JWS_SIGNING_ALG"                         = "${local.secret_prefix}sbmtd-agency-jws-signing-alg)"
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
