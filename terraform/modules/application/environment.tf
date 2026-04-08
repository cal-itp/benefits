# The Container App Environment
resource "azurerm_container_app_environment" "main" {
  name                           = "CAE-CDT-PUB-VIP-CALITP-${var.env_letter}-001"
  location                       = var.location
  resource_group_name            = var.resource_group_name
  log_analytics_workspace_id     = var.log_analytics_workspace_id
  infrastructure_subnet_id       = var.infrastructure_subnet_id
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

# Manages the 'benefits-storage' file share of the Container App Environment
resource "azurerm_container_app_environment_storage" "main" {
  name                         = "benefits-storage"
  container_app_environment_id = azurerm_container_app_environment.main.id
  account_name                 = var.storage_account_name
  access_key                   = var.storage_account_access_key
  share_name                   = var.storage_share_name
  access_mode                  = "ReadWrite"
}
