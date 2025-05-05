resource "azurerm_key_vault" "kv" {
  name                       = "${var.kv_name}-${var.project-sufix}"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  enable_rbac_authorization = true
}

resource "azurerm_role_assignment" "app_identity_keyvault_secrets_reader" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_linux_web_app.webapp.identity[0].principal_id
}

resource "azurerm_role_assignment" "terraform_identity_keyvault_secrets_manager" {
  scope                = azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}
value        = var.db_admin_user

resource "azurerm_key_vault_secret" "db_user" {
  name         = "DatabaseUser"
  key_vault_id = azurerm_key_vault.kv.id
  content_type = "text/plain"
}

resource "azurerm_key_vault_secret" "db_password" {
  value        = var.db_admin_password
  name         = "DatabasePassword"
  key_vault_id = azurerm_key_vault.kv.id
  content_type = "text/plain"
}

resource "azurerm_key_vault_secret" "db_name_secret" {
  name         = "DatabaseName"
  value        = var.db_name
  key_vault_id = azurerm_key_vault.kv.id
  content_type = "text/plain"
}

resource "azurerm_key_vault_secret" "secret_key" {
  name         = "SecretKey"
  value        = var.db_admin_password  
  key_vault_id = azurerm_key_vault.kv.id
  content_type = "text/plain"
}

