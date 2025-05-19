terraform {
  # Define which plugins (providers) are needed.
  required_providers {
    # Use the Azure provider plugin.
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.27.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  # Minimum required version of Terraform.
  required_version = ">= 1.1.0"

  # Configure Azure backend for state management
  backend "azurerm" {
    resource_group_name  = "resource-group-ls-p-mexc-1"
    storage_account_name = "lspmexc1storageacc54"
    container_name       = "tfstate"
    key                  = "prod/legends-shop/terraform.tfstate"
  }
}
# Configure the Azure provider plugin.
provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}
