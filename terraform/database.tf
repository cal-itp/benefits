locals {
  postgres_admin_password_secret_name = "postgres-admin-password"
}

# Manage an Azure Database for PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "main" {
  name                = "adb-cdt-pub-vip-calitp-${lower(local.env_letter)}-db"
  resource_group_name = data.azurerm_resource_group.main.name
  location            = data.azurerm_resource_group.main.location
  sku_name            = "B_Standard_B1ms"
  storage_mb          = 32768 # 32GB
  storage_tier        = "P4"
  version             = "17"

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  authentication {
    active_directory_auth_enabled = false
    password_auth_enabled         = true
  }
  public_network_access_enabled = false
  private_dns_zone_id           = azurerm_private_dns_zone.db.id # https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/postgresql_flexible_server#private_dns_zone_id-1
  delegated_subnet_id           = azurerm_subnet.main["DB"].id
  administrator_login           = "postgres_admin"
  administrator_password        = azurerm_key_vault_secret.postgres_admin_password.value

  lifecycle {
    ignore_changes = [tags]
  }
}

# Generate a random password for PostgreSQL
resource "random_password" "postgres_admin_password" {
  length           = 32
  min_lower        = 4
  min_upper        = 4
  min_numeric      = 4
  min_special      = 4
  special          = true
  override_special = "_%@!-"
}

# Create the secret for PostgreSQL Admin Password using the generated password
resource "azurerm_key_vault_secret" "postgres_admin_password" {
  name         = local.postgres_admin_password_secret_name
  value        = random_password.postgres_admin_password.result
  key_vault_id = azurerm_key_vault.main.id
  content_type = "password"
  depends_on = [
    random_password.postgres_admin_password # Ensure password is generated first
  ]
}
