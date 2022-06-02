terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.7.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "RG-CDT-PUB-VIP-CALITP-D-001"
    storage_account_name = "sacalitpd001"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
}

data "azurerm_resource_group" "benefits" {
  name = "RG-CDT-PUB-VIP-CALITP-D-001"
}
