locals {
  # VNet uses a shared resource group different from the main App Service resource group
  network_resource_group_name = "RG-CDT-PUB-SHRD-W-P-001"
}

data "azurerm_subnet" "main" {
  name                 = "SNET-CDT-PUB-CALITP-P-001"
  virtual_network_name = "VNET-CDT-PUB-SHRD-W-P-001"
  resource_group_name  = local.network_resource_group_name
}

resource "azurerm_app_service_environment_v3" "main" {
  name                = "ASE-CDT-PUB-CALITP-P-001"
  resource_group_name = local.network_resource_group_name
  subnet_id           = data.azurerm_subnet.main.id

  # override the default Cipher suite as a remediation to vulnerability scanning
  # https://github.com/cal-itp/benefits/issues/771
  cluster_setting {
    name  = "FrontEndSSLCipherSuiteOrder"
    value = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
