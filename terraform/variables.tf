variable "resource_group_name" {
  default = "myTFResourceGroup"
}

variable "vnet_name" {
  default = "myTFVnet"
}

variable "service_plan_name" {
  default = "legendsShop-service_plan"
}

variable "web_app_name" {
  default = "LegendsShop"
}

variable "location" {
  default = "mexicocentral"
}

variable "docker_image_name_backend" {
  default = "jonathanhn/dockerhub:legeshop-backend"
}
