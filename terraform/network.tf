locals {
  # VNet uses a shared resource group different from the main App Service resource group
  network_resource_group_name = "RG-CDT-PUB-SHRD-W-${local.env_letter}-001"
}

data "azurerm_subnet" "main" {
  name                 = "SNET-CDT-PUB-CALITP-${local.env_letter}-001"
  virtual_network_name = "VNET-CDT-PUB-SHRD-W-${local.env_letter}-001"
  resource_group_name  = local.network_resource_group_name
}
