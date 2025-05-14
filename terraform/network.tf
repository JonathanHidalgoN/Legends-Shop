#This is the general virtual network 
resource "azurerm_virtual_network" "vnet" {
  name                = "${var.vnet_name}-${var.project-sufix}"
  address_space       = var.vnet_address_space
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# Dedicated subnet for the database (required for VNet integration)
resource "azurerm_subnet" "db_subnet" {
  name                 = "database-subnet-${var.project-sufix}"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = var.subnet_database_adress_space
  #This is like setting a policy telling the subnet that only flexible server 
  #will use this subnet 
  delegation {
    name = "delegation"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

#subnet for the web app
resource "azurerm_subnet" "webapp_subnet" {
  name                 = "webapp-subnet-${var.project-sufix}"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = var.subnet_webapp_adress_space

  delegation {
    name = "webapp-delegation"
    service_delegation {
      name    = "Microsoft.Web/serverFarms"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }
  }
}

#VNet integration for the web app
resource "azurerm_app_service_virtual_network_swift_connection" "webapp_vnet_integration" {
  app_service_id = azurerm_linux_web_app.webapp.id
  subnet_id      = azurerm_subnet.webapp_subnet.id
}
