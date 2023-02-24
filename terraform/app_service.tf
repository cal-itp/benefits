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

  storage_account {
    access_key   = azurerm_storage_account.main.primary_access_key
    account_name = azurerm_storage_account.main.name
    name         = "benefits-config"
    type         = "AzureBlob"
    share_name   = azurerm_storage_container.config.name
    mount_path   = "/home/calitp/app/config"
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

    "ANALYTICS_KEY" = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=analytics-key)",

    # Django settings
    "DJANGO_ADMIN"            = local.is_prod ? "false" : "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=django-admin)",
    "DJANGO_ALLOWED_HOSTS"    = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=django-allowed-hosts)",
    "DJANGO_DEBUG"            = local.is_prod ? "false" : "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=django-debug)",
    "DJANGO_LOAD_SAMPLE_DATA" = "false",
    "DJANGO_LOG_LEVEL"        = "DEBUG",
    "DJANGO_MIGRATIONS_DIR"   = "./config",

    "DJANGO_RATE_LIMIT"         = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=django-rate-limit)",
    "DJANGO_RATE_LIMIT_METHODS" = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=django-rate-limit-methods)",
    "DJANGO_RATE_LIMIT_PERIOD"  = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=django-rate-limit-period)",

    "DJANGO_RECAPTCHA_SECRET_KEY" = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=django-recaptcha-secret-key)",
    "DJANGO_RECAPTCHA_SITE_KEY"   = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=django-recaptcha-site-key)",

    "DJANGO_SECRET_KEY"      = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=django-secret-key)",
    "DJANGO_TRUSTED_ORIGINS" = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=django-trusted-origins)",

    "HEALTHCHECK_USER_AGENTS" = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=healthcheck-user-agents)",

    # Sentry
    "SENTRY_DSN"         = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=sentry-dsn)",
    "SENTRY_ENVIRONMENT" = local.env_name,

    # Environment variables for data migration
    "MST_SENIOR_GROUP_ID"                            = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=mst-senior-group-id)",
    "MST_COURTESY_CARD_GROUP_ID"                     = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=mst-courtesy-card-group-id)"
    "SACRT_SENIOR_GROUP_ID"                          = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=sacrt-senior-group-id)"
    "CLIENT_PRIVATE_KEY"                             = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=client-private-key)"
    "CLIENT_PUBLIC_KEY"                              = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=client-public-key)"
    "SERVER_PUBLIC_KEY_URL"                          = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=server-public-key-url)"
    "PAYMENT_PROCESSOR_CLIENT_CERT"                  = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-client-cert)"
    "PAYMENT_PROCESSOR_CLIENT_CERT_PRIVATE_KEY"      = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-client-cert-private-key)"
    "PAYMENT_PROCESSOR_CLIENT_CERT_ROOT_CA"          = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-client-cert-root-ca)"
    "AUTH_PROVIDER_CLIENT_NAME"                      = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=auth-provider-client-name)"
    "AUTH_PROVIDER_CLIENT_ID"                        = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=auth-provider-client-id)"
    "AUTH_PROVIDER_AUTHORITY"                        = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=auth-provider-authority)"
    "AUTH_PROVIDER_SCOPE"                            = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=auth-provider-scope)"
    "AUTH_PROVIDER_CLAIM"                            = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=auth-provider-claim)"
    "MST_OAUTH_VERIFIER_NAME"                        = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=mst-oauth-verifier-name)"
    "COURTESY_CARD_VERIFIER"                         = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=courtesy-card-verifier)"
    "COURTESY_CARD_VERIFIER_API_URL"                 = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=courtesy-card-verifier-api-url)"
    "COURTESY_CARD_VERIFIER_API_AUTH_HEADER"         = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=courtesy-card-verifier-api-auth-header)"
    "COURTESY_CARD_VERIFIER_API_AUTH_KEY"            = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=courtesy-card-verifier-api-auth-key)"
    "COURTESY_CARD_VERIFIER_JWE_CEK_ENC"             = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=courtesy-card-verifier-jwe-cek-enc)"
    "COURTESY_CARD_VERIFIER_JWE_ENCRYPTION_ALG"      = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=courtesy-card-verifier-jwe-encryption-alg)"
    "COURTESY_CARD_VERIFIER_JWS_SIGNING_ALG"         = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=courtesy-card-verifier-jws-signing-alg)"
    "SACRT_OAUTH_VERIFIER_NAME"                      = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=sacrt-oauth-verifier-name)"
    "PAYMENT_PROCESSOR_NAME"                         = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-name)"
    "PAYMENT_PROCESSOR_API_BASE_URL"                 = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-api-base-url)"
    "PAYMENT_PROCESSOR_API_ACCESS_TOKEN_ENDPOINT"    = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-api-access-token-endpoint)"
    "PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_KEY" = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-api-access-token-request-key)"
    "PAYMENT_PROCESSOR_API_ACCESS_TOKEN_REQUEST_VAL" = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-api-access-token-request-val)"
    "PAYMENT_PROCESSOR_CARD_TOKENIZE_URL"            = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-card-tokenize-url)"
    "PAYMENT_PROCESSOR_CARD_TOKENIZE_FUNC"           = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-card-tokenize-func)"
    "PAYMENT_PROCESSOR_CARD_TOKENIZE_ENV"            = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=payment-processor-card-tokenize-env)"
    "MST_AGENCY_SHORT_NAME"                          = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=mst-agency-short-name)"
    "MST_AGENCY_LONG_NAME"                           = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=mst-agency-long-name)"
    "MST_AGENCY_JWS_SIGNING_ALG"                     = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=mst-agency-jws-signing-alg)"
    "SACRT_AGENCY_SHORT_NAME"                        = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=sacrt-agency-short-name)"
    "SACRT_AGENCY_LONG_NAME"                         = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=sacrt-agency-long-name)"
    "SACRT_AGENCY_MERCHANT_ID"                       = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=sacrt-agency-merchant-id)"
    "SACRT_AGENCY_JWS_SIGNING_ALG"                   = "@Microsoft.KeyVault(VaultName=KV-CDT-PUB-CALITP-${local.env_letter}-001;SecretName=sacrt-agency-jws-signing-alg)"
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
