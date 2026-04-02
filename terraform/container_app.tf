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
