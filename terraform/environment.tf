locals {
  is_prod    = terraform.workspace == "default"
  env_name   = local.is_prod ? "prod" : terraform.workspace
  env_letter = upper(substr(local.env_name, 0, 1))

  # non-production is <env>-benefits.calitp.org
  hostname_prefix = local.is_prod ? "" : "${local.env_name}-"
  hostname        = "${local.hostname_prefix}benefits.calitp.org"
}

data "azurerm_resource_group" "main" {
  name = "RG-CDT-PUB-VIP-CALITP-${local.env_letter}-001"
}
