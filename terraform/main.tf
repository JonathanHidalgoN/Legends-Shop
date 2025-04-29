# Configure Terraform itself.
terraform {
  # Define which plugins (providers) are needed.
  required_providers {
    # Use the Azure provider plugin.
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.27.0"
    }
  }

  # Minimum required version of Terraform.
  required_version = ">= 1.1.0"
}

# Configure the Azure provider plugin.
# It will use credentials from your environment (like `az login`).
provider "azurerm" {
  features {}
}

# Fetch information about the Azure identity running Terraform.
data "azurerm_client_config" "current" {}
# Gets details like your tenant ID and object ID.

# Create a random unique identifier (UUID).
resource "random_uuid" "role_assignment_name_namespace" {}

# Create an Azure Resource Group - a container for resources.
resource "azurerm_resource_group" "rg" {
  name      = var.resource_group_name
  location = var.location

  tags = {
    Environment = "Legends Shop"
    Team        = "DevOps"
  }
}

# Create an Azure App Service Plan - provides hosting resources for web apps.
resource "azurerm_service_plan" "appserviceplan" {
  name                = var.service_plan_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "F1"
}

# Create an Azure Key Vault - securely store secrets, keys, certificates.
resource "azurerm_key_vault" "kv" {
  name                        = "my-secure-app-secrets-kv"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
}

# Create an Azure Linux Web App - where your application code runs.
resource "azurerm_linux_web_app" "webapp" {
  name                  = var.web_app_name
  location              = azurerm_resource_group.rg.location
  resource_group_name   = azurerm_resource_group.rg.name
  service_plan_id       = azurerm_service_plan.appserviceplan.id
  https_only            = true # Force HTTPS.

  # Configure a System-Assigned Managed Identity for the web app.
  # Allows the app to access other Azure resources securely without secrets.
  identity {
    type = "SystemAssigned"
  }

  # Web app runtime and behavior settings.
  site_config {
    minimum_tls_version = "1.2"
    always_on           = false

    # Configure the application stack (using Docker).
    application_stack {
      docker_image_name = var.docker_image_name_backend
    }
  }

  # Application settings (environment variables).
  app_settings = {
    "WEBSITES_PORT"      = "8000" # Port the app listens on (common for Docker).
    # Example of referencing a secret from Key Vault:
    # "DATABASE_PASSWORD"  = "@Microsoft.KeyVault(VaultName=${azurerm_key_vault.kv.name};SecretName=DatabasePassword)"
  }
}

# Create an Azure Role Assignment - grants permissions to an identity.
resource "azurerm_role_assignment" "app_identity_keyvault_secrets_reader" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Reader"
  principal_id         = azurerm_linux_web_app.webapp.identity[0].principal_id
  name                 = random_uuid.role_assignment_name_namespace.id
}

# Create an Azure Virtual Network (VNet) - creates a private network in the cloud.
resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name # VNet name from variable.
  address_space       = ["10.0.0.0/16"] # Private IP range for the VNet.
  location            = azurerm_resource_group.rg.location # Same region as RG.
  resource_group_name = azurerm_resource_group.rg.name # Link to the RG.
}
