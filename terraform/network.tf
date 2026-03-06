locals {
  # VNet uses a shared Resource Group, different from App Service Resource Group we use for Benefits stuff
  network_resource_group_name = "RG-CDT-PUB-SHRD-W-P-001"
  vnet_name                   = "VNET-CDT-PUB-SHRD-W-P-001"
  subnet_name                 = local.is_prod ? "SNET-CDT-PUB-CALITP-P-001" : "SN-CDT-PUB-CALITP-${local.env_letter}-001"

  # use the subnet ID rather than referencing it as a data source to work around permissions issues
  subnet_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${local.network_resource_group_name}/providers/Microsoft.Network/virtualNetworks/${local.vnet_name}/subnets/${local.subnet_name}"

  subnet_prefix = "SNET-CDT-PUB-VIP-CALITP-${local.env_letter}"
  network_subnets = {
    "APP" = {
      prefix     = ["10.0.0.0/26"] # 64 addresses - 10.0.4.0 to 10.0.4.63
      delegation = "Microsoft.Web/serverFarms"
    }
    "DB" = {
      prefix     = ["10.0.0.64/26"] # 64 addresses - 10.0.0.64 to 10.0.0.127
      delegation = "Microsoft.DBforPostgreSQL/flexibleServers"
    }
  }
}

# The primary VNet (per environment)
resource "azurerm_virtual_network" "main" {
  name                = "VNET-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
  location            = data.azurerm_resource_group.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  address_space       = ["10.0.0.0/24"] # 256 addresses - 10.0.0.0 to 10.0.0.255

  lifecycle {
    ignore_changes = [tags]
  }
}

# The subnets for the primary VNet
resource "azurerm_subnet" "main" {
  # This for_each loop creates a subnet for each item in the network_subnets map.
  for_each = local.network_subnets

  name                 = "${local.subnet_prefix}-${each.key}"
  virtual_network_name = azurerm_virtual_network.main.name
  resource_group_name  = data.azurerm_resource_group.main.name
  address_prefixes     = each.value.prefix

  delegation {
    name = "delegation-${lower(each.key)}"
    service_delegation {
      name = each.value.delegation
    }
  }

  default_outbound_access_enabled = false
}
