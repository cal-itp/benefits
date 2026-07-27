terraform {
  // see version in .github/workflows/deploy.yml

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.67"
    }
  }

  backend "azurerm" {
    resource_group_name  = "RG-CDT-PUB-VIP-CALITP-P-001"
    storage_account_name = "sacdtcalitpp001"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}

provider "azurerm" {
  subscription_id = var.ARM_SUBSCRIPTION_ID
  features {}
}

data "azurerm_client_config" "current" {}
