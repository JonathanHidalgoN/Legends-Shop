resource "azurerm_postgresql_flexible_server" "db_server" {
  name                = "${var.db_server_name}-${var.project-sufix}"
  resource_group_name = azurerm_resource_group.rg.name
  administrator_login = var.db_admin_user
  location            = azurerm_resource_group.rg.location

  administrator_password = var.db_admin_password

  sku_name   = "B_Standard_B1ms"
  storage_mb = 32768
  version    = "14"

  #This is the action, telling the server there is a subnet to use.
  #The subnet then has a policy where only this kind of service can use it 
  private_dns_zone_id           = azurerm_private_dns_zone.db_zone.id
  delegated_subnet_id           = azurerm_subnet.db_subnet.id
  public_network_access_enabled = false
}

resource "azurerm_postgresql_flexible_server_database" "database" {
  # Corrected resource type name
  name      = var.db_name
  server_id = azurerm_postgresql_flexible_server.db_server.id
  charset   = "UTF8"
}

resource "azurerm_private_dns_zone" "db_zone" {
  # Required for private endpoint connection to database from VNet
  name                = var.dns_database_server_link
  resource_group_name = azurerm_resource_group.rg.name
}

#It tells your VNet's DNS resolver to forward any queries for 
#names ending in privatelink.postgres.database.azure.com to the Azure Private DNS service,
resource "azurerm_private_dns_zone_virtual_network_link" "db_zone_link" {
  name                  = "${var.db_server_name}-${var.project-sufix}-link"
  private_dns_zone_name = azurerm_private_dns_zone.db_zone.name
  virtual_network_id    = azurerm_virtual_network.vnet.id
  resource_group_name   = azurerm_resource_group.rg.name
}
