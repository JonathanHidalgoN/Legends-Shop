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

  # TODO:Configure remote state backend (RECOMMENDED for production)
}

# Configure the Azure provider plugin.
provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}
