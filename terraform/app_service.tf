resource "azurerm_service_plan" "appserviceplan" {
  name                = "${var.service_plan_name}-${var.project-sufix}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"
  sku_name            = "F1"
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
     always_on = false
    application_stack {
      docker_image_name = var.docker_image_name_backend
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
    # "DATABASE_CONNECTION_STRING" = "@Microsoft.KeyVault(VaultName=${azurerm_key_vault.kv.name};SecretName=DatabaseConnectionString)"
  })

}
