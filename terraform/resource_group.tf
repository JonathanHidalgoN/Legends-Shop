resource "azurerm_resource_group" "rg" {
  name     = "${var.resource_group_name}-${var.project-sufix}"
  location = var.location

  tags = {
    Environment = "Dev"
    Team        = "DevOps"
    Project     = "LegendsShop"
  }
}
