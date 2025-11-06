terraform {
  // see version in azure-pipelines.yml

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  backend "azurerm" {
    # needs to match azure-pipelines.yml
    resource_group_name  = "RG-CDT-PUB-VIP-CALITP-P-001"
    storage_account_name = "sacdtcalitpp001"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}

provider "azurerm" {
  subscription_id = local.is_prod ? var.ARM_SUBSCRIPTION_ID : var.ARM_DEV_SUBSCRIPTION_ID
  features {}
}

data "azurerm_client_config" "current" {}
