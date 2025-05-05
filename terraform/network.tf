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
