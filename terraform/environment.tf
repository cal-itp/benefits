locals {
  is_prod             = terraform.workspace == "default"
  is_test             = terraform.workspace == "test"
  is_dev              = !(local.is_prod || local.is_test)
  env_name            = local.is_prod ? "prod" : terraform.workspace
  env_letter          = upper(substr(local.env_name, 0, 1))
  subscription_letter = local.is_prod ? "P" : "D"
  hostname            = local.is_prod ? "benefits.calitp.org" : "${local.env_name}-benefits.calitp.org"
}

data "azurerm_resource_group" "main" {
  name = "RG-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
}
