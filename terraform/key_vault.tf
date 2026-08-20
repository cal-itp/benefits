locals {
  # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/key_vault#certificate_permissions
  all_certificate_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "ManageContacts",
    "ManageIssuers",
    "GetIssuers",
    "ListIssuers",
    "SetIssuers",
    "DeleteIssuers",
  ]

  all_key_permissions = [
    "Get",
    "List",
    "Update",
    "Create",
    "Import",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
    "GetRotationPolicy",
    "SetRotationPolicy",
    "Rotate",
  ]

  all_secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete",
    "Recover",
    "Backup",
    "Restore",
  ]

  key_vault_name              = "KV-CDT-PUB-CALITP-${local.env_letter}-001"
  key_vault_secret_uri_prefix = "https://${local.key_vault_name}.vault.azure.net/secrets"
}

resource "azurerm_key_vault" "main" {
  name                       = local.key_vault_name
  location                   = data.azurerm_resource_group.main.location
  resource_group_name        = data.azurerm_resource_group.main.name
  sku_name                   = "standard"
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  purge_protection_enabled   = true
  rbac_authorization_enabled = false

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      tags,
      access_policy # IMPORTANT: Tell Terraform to ignore changes to access policies here since we aren't using inline policies
    ]
  }
}

# Standalone Access Policy for Engineering Group
resource "azurerm_key_vault_access_policy" "engineering" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.ENGINEERING_GROUP_OBJECT_ID

  certificate_permissions = local.all_certificate_permissions
  key_permissions         = local.all_key_permissions
  secret_permissions      = local.all_secret_permissions

  # This ensures the Key Vault itself is created before trying to attach a policy.
  depends_on = [azurerm_key_vault.main]
}

# Standalone Access Policies for GH Actions Service Principals

resource "azurerm_key_vault_access_policy" "devsecops_apply" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.sp_apply_object_id

  secret_permissions = local.all_secret_permissions

  # This ensures the Key Vault itself is created before trying to attach a policy.
  depends_on = [azurerm_key_vault.main]
}

resource "azurerm_key_vault_access_policy" "devsecops_plan" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = var.sp_plan_object_id

  secret_permissions = ["Get", "List"]

  # This ensures the Key Vault itself is created before trying to attach a policy.
  depends_on = [azurerm_key_vault.main]
}

# https://learn.microsoft.com/en-us/azure/app-service/app-service-key-vault-references?tabs=azure-cli#granting-your-app-access-to-key-vault
# Standalone Access Policy for the Benefits (web) Container App's Managed Identity
resource "azurerm_key_vault_access_policy" "web_container_app" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = module.application.web_principal_id

  secret_permissions = ["Get"]

  # This ensures the Key Vault itself is created before trying to attach a policy.
  depends_on = [azurerm_key_vault.main]
}

# Standalone Access Policy for the pgAdmin Container App's Managed Identity
resource "azurerm_key_vault_access_policy" "pgadmin_container_app" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = module.application.pgadmin_principal_id

  secret_permissions = ["Get"]

  # This ensures the Key Vault itself is created before trying to attach a policy.
  depends_on = [azurerm_key_vault.main]
}

# these declarations can be removed as soon as the application service has been torn down in the production env
moved {
  from = random_password.django_db_password
  to   = module.application.random_password.django_db_password
}

moved {
  from = azurerm_key_vault_secret.django_db_password
  to   = module.application.azurerm_key_vault_secret.django_db_password
}
