terraform {
  // see version in azure-pipelines.yml

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }

    dotenv = {
      source  = "jrhouston/dotenv"
      version = "~> 1.0"
    }

    github = {
      source  = "integrations/github"
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
  features {}
}

provider "github" {
  token = var.github_token
  owner = "cal-itp"
}

data "azurerm_client_config" "current" {}
