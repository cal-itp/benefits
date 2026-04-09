locals {
  django_storage_dir_path  = "/calitp/app/data"
  pgadmin_storage_dir_path = "/var/lib/pgadmin"
  app_config_secrets = {
    # Amplitude
    "analytics-key" = { env_name = "ANALYTICS_KEY", exists = !var.is_dev }, # Only create env var in non-dev environments
    # Django Azure Email Backend
    (var.azure_communication_connection_string_name) = { env_name = "AZURE_COMMUNICATION_CONNECTION_STRING", exists = true },
    # Django settings
    "django-allowed-hosts"               = { env_name = "DJANGO_ALLOWED_HOSTS", exists = true },
    "django-debug"                       = { env_name = "DJANGO_DEBUG", exists = !var.is_prod }, # Only create secret in non-prod environments
    "django-log-level"                   = { env_name = "DJANGO_LOG_LEVEL", exists = true },
    "django-recaptcha-secret-key"        = { env_name = "DJANGO_RECAPTCHA_SECRET_KEY", exists = true },
    "django-recaptcha-site-key"          = { env_name = "DJANGO_RECAPTCHA_SITE_KEY", exists = true },
    "django-secret-key"                  = { env_name = "DJANGO_SECRET_KEY", exists = true },
    "django-trusted-origins"             = { env_name = "DJANGO_TRUSTED_ORIGINS", exists = true },
    "django-db-name"                     = { env_name = "DJANGO_DB_NAME", exists = true },
    "django-db-user"                     = { env_name = "DJANGO_DB_USER", exists = true },
    (var.django_db_password_secret_name) = { env_name = "DJANGO_DB_PASSWORD", exists = true },
    # Postgres settings
    "use-postgres"                            = { env_name = "USE_POSTGRES", exists = true },
    (var.postgres_admin_password_secret_name) = { env_name = "POSTGRES_PASSWORD", exists = true },
    "healthcheck-user-agents"                 = { env_name = "HEALTHCHECK_USER_AGENTS", exists = !var.is_dev }, # Only create secret in non-dev environments
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
    "DEFAULT_FROM_EMAIL" = var.sender_email,
    # Django settings
    "DJANGO_STORAGE_DIR" = local.django_storage_dir_path,
    # Database settings
    "POSTGRES_HOSTNAME" = var.postgres_fqdn,
    "POSTGRES_DB"       = var.postgres_admin_db,
    "POSTGRES_USER"     = var.postgres_admin_login,
    # Sentry
    "SENTRY_ENVIRONMENT" = var.env_name
  }
}
