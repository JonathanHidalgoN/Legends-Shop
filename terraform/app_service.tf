resource "azurerm_service_plan" "appserviceplan" {
  name                = "${var.service_plan_name}-${var.project-sufix}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "webapp" {
  name                = "${var.web_app_name}-${var.project-sufix}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.appserviceplan.id
  https_only          = true

  identity {
    type = "SystemAssigned"
  }

  site_config {
    minimum_tls_version = "1.2"
    always_on           = true

    application_stack {
      docker_image_name = var.docker_image_name_backend
    }

    ip_restriction {
      name                      = "vnet-integration"
      action                    = "Allow"
      priority                  = 100
      virtual_network_subnet_id = azurerm_subnet.webapp_subnet.id
    }

    ip_restriction {
      name       = "dev-ip"
      action     = "Allow"
      priority   = 200
      ip_address = "${var.development_ip}/32"
    }

    ip_restriction {
      name       = "vercel-ip"
      action     = "Allow"
      priority   = 300
      ip_address = "${var.vercel_ip}/32"
    }

    ip_restriction {
      name        = "deny-all-other"
      action      = "Deny"
      priority    = 2147483647
      description = "Deny all other traffic"
    }
  }


  # Application settings (environment variables for the app).
  # --- Use Key Vault references here for runtime secret retrieval by the app ---
  app_settings = merge(var.web_app_settings, { # Merge with base settings from variables.tf
    "DATABASE_HOST"     = azurerm_postgresql_flexible_server.db_server.fqdn
    "DATABASE_USER"     = "@Microsoft.KeyVault(VaultName=${azurerm_key_vault.kv.name};SecretName=DatabaseUser)"
    "DATABASE_PASSWORD" = "@Microsoft.KeyVault(VaultName=${azurerm_key_vault.kv.name};SecretName=DatabasePassword)"
    "DATABASE_NAME"     = "@Microsoft.KeyVault(VaultName=${azurerm_key_vault.kv.name};SecretName=DatabaseName)"
    "SECRET_KEY"        = "@Microsoft.KeyVault(VaultName=${azurerm_key_vault.kv.name};SecretName=SecretKey)"
    "ON_AZURE"          = "true"
  })

}
