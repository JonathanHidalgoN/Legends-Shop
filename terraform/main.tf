terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.27.0"
    }
  }

  required_version = ">= 1.1.0"
}

provider "azurerm" {
  features {}
}

data "azurerm_client_config" "current" {}

resource "random_uuid" "role_assignment_name_namespace" {}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    Environment = "Legends Shop"
    Team        = "DevOps"
  }
}

resource "azurerm_service_plan" "appserviceplan" {
  name                = var.service_plan_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "F1" # F1 is the free tier
}

resource "azurerm_key_vault" "kv" {
  name                        = "my-secure-app-secrets-kv"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
}

resource "azurerm_linux_web_app" "webapp" {
  name                 = var.web_app_name
  location             = azurerm_resource_group.rg.location
  resource_group_name  = azurerm_resource_group.rg.name
  service_plan_id      = azurerm_service_plan.appserviceplan.id
  https_only           = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    minimum_tls_version = "1.2"
    always_on           = false 

    application_stack {
      docker_image_name = var.docker_image_name_backend
    }
  }

  app_settings = {
    "WEBSITES_PORT"      = "8000"
    # "DATABASE_PASSWORD"  = "@Microsoft.KeyVault(VaultName=${azurerm_key_vault.kv.name};SecretName=DatabasePassword)"
  }
}

resource "azurerm_role_assignment" "app_identity_keyvault_secrets_reader" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Reader"
  principal_id         = data.azurerm_client_config.current.object_id
  name = random_uuid.role_assignment_name_namespace.id
}

resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

