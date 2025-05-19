output "resource_group_name" {
  description = "Name of the deployed Resource Group."
  value       = azurerm_resource_group.rg.name
}

output "web_app_default_hostname" {
  description = "Default hostname of the Web App."
  value       = azurerm_linux_web_app.webapp.default_hostname
}

output "key_vault_uri" {
  description = "URI of the Key Vault."
  value       = azurerm_key_vault.kv.vault_uri
}

output "db_server_fqdn" {
  description = "Fully qualified domain name of the PostgreSQL Flexible Server."
  value       = azurerm_postgresql_flexible_server.db_server.fqdn
}

