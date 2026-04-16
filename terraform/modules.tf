module "application" {
  source = "./modules/application"

  # Terraform Environment
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location
  env_letter          = local.env_letter
  env_name            = local.env_name
  is_dev              = local.is_dev
  is_prod             = local.is_prod

  # Monitoring
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id

  # Network
  subnet_ca_id = azurerm_subnet.main["CA"].id

  # Storage
  storage_account_name       = azurerm_storage_account.main.name
  storage_account_access_key = azurerm_storage_account.main.primary_access_key
  storage_share_web_name     = azurerm_storage_share.web.name
  storage_share_pgadmin_name = azurerm_storage_share.pgadmin.name

  # Benefits Container App Image Details
  container_registry   = var.CONTAINER_REGISTRY
  container_repository = var.CONTAINER_REPOSITORY
  container_tag        = var.CONTAINER_TAG

  # Key Vault
  key_vault_secret_uri_prefix = local.key_vault_secret_uri_prefix

  # App Config
  azure_communication_connection_string_name = local.azure_communication_connection_string_name
  django_db_password_secret_name             = local.django_db_password_secret_name
  postgres_admin_password_secret_name        = local.postgres_admin_password_secret_name
  sender_email                               = local.sender_email
  postgres_fqdn                              = azurerm_postgresql_flexible_server.main.fqdn
  postgres_admin_login                       = local.postgres_admin_login
  postgres_admin_db                          = local.postgres_admin_db

  # pgAdmin Config
  pgadmin_admin_password_secret_name = local.pgadmin_admin_password_secret_name
  pgadmin_config_db_uri_secret_name  = local.pgadmin_config_db_uri_secret_name
}
