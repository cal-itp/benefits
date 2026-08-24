terraform {
  // see version in .github/workflows/deploy.yml

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.2.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "RG-CDT-PUB-VIP-CALITP-P-001"
    storage_account_name = "sacdtcalitpp001"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}

// subscription_id is inferred from the active Azure CLI session
provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}
