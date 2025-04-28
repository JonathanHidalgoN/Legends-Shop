terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.27.0"
    }
  }

  required_version = ">= 1.1.0"
}

# Provider configuration - tells Terraform to use Azure as the provider
provider "azurerm" {
  features {}
}

# Resource Group creation - all Azure resources need to be inside a resource group
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Environment = "Legends Shop"
    Team        = "DevOps"
  }
}

# Service Plan creation - defines the hosting environment for the app
resource "azurerm_service_plan" "appserviceplan" {
  name                = var.service_plan_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "F1" # F1 is the free tier
}

resource "azurerm_linux_web_app" "webapp" {
  name                 = var.web_app_name
  location             = azurerm_resource_group.rg.location
  resource_group_name  = azurerm_resource_group.rg.name
  service_plan_id      = azurerm_service_plan.appserviceplan.id
  https_only           = true
  site_config {
    minimum_tls_version = "1.2"
    always_on           = false 

    application_stack {
      docker_image_name = var.docker_image_name_backend
    }
  }

  app_settings = {
    "WEBSITES_PORT" = "8000"
  }
}

resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

