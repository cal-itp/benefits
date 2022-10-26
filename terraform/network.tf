locals {
  # VNet uses a shared Resource Group, different from App Service Resource Group we use for Benefits stuff
  network_resource_group_name = local.is_prod ? "RG-CDT-PUB-SHRD-W-P-001" : "RG-CDT-PUB-D-001"
  vnet_name                   = local.is_prod ? "VNET-CDT-PUB-SHRD-W-P-001" : "VNET-CDT-PUB-D-001"
  subnet_name                 = local.is_prod ? "SNET-CDT-PUB-CALITP-P-001" : "SN-CDT-PUB-CALITP-${local.env_letter}-001"

  subnet_id = "/subscriptions/${data.azurerm_client_config.current.subscription_id}/resourceGroups/${local.network_resource_group_name}/providers/Microsoft.Network/virtualNetworks/${local.vnet_name}/subnets/${local.subnet_name}"
}
