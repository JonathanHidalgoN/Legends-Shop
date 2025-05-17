variable "project-sufix" {
  description = "Project sufix"
  type        = string
  default     = "ls-p-mexc-1"
}

variable "resource_group_name" {
  description = "Name of the Azure Resource Group, has to match name in setup file"
  type        = string
  default     = "resource-group-ls-p-mexc-1"
}

variable "location" {
  description = "Azure region for deployment, has to match name in setup file"
  type        = string
  default     = "mexicocentral"
}

variable "dns_database_server_link" {
  description = "Link to connect with the vn to the database"
  type        = string
  default     = "privatelink.postgres.database.azure.com"
}

variable "kv_name" {
  description = "Name of the Azure Key Vault."
  type        = string
  default     = "key-vault"
}

variable "db_server_name" {
  description = "Name of the PostgreSQL Flexible Server."
  type        = string
  default     = "db-server"
}

variable "db_name" {
  description = "Name of the PostgreSQL Database."
  type        = string
  default     = "legends-shop-db"
}

variable "db_admin_password" {
  description = "Password for the PostgreSQL admin user. MUST be provided securely (e.g., environment variable TF_VAR_db_admin_password)."
  type        = string
  sensitive   = true
}

variable "db_admin_user" {
  description = "Username for the PostgreSQL admin user."
  type        = string
  default     = "dbadmin"
}

variable "service_plan_name" {
  description = "Name of the App Service Plan."
  type        = string
  default     = "service-plan"
}

variable "web_app_name" {
  description = "Name of the Linux Web App."
  type        = string
  default     = "Legends-shop"
}

#TODO: how to keep this pointing to latest?
variable "docker_image_name_backend" {
  description = "Docker image name for the backend web app."
  type        = string
  default     = "jonathanhn/leageshop-backend:latest"
}

variable "web_app_settings" {
  description = "Additional application settings for the web app."
  type        = map(string)
  default = {
    "WEBSITES_PORT"               = "8000"
    "DATABASE_PORT"               = "5432"
    "DATABASE_DIALECT"            = "postgresql"
    "FRONTEND_HOST"               = "https://legends-shop.vercel.app/"
    "FRONTEND_PORT"               = "3000"
    "ALGORITHM"                   = "HS256"
    "ACCESS_TOKEN_EXPIRE_MINUTES" = "30"
    "LOG_DIR_NAME"                = "backend_logs"
  }
}

variable "vnet_name" {
  description = "Name of the Virtual Network."
  type        = string
  default     = "vnet"
}

variable "vnet_address_space" {
  description = "Address space for the Virtual Network."
  type        = list(string)
  default     = ["192.168.0.0/16"] # Covers 192.168.0.0 - 192.168.255.255
}

variable "subnet_database_adress_space" {
  description = "Address space for the database subnet."
  type        = list(string)
  default     = ["192.168.0.0/24"] # Covers 192.168.0.0 - 192.168.0.255
}

variable "subnet_webapp_adress_space" {
  description = "Address space for the web app subnet."
  type        = list(string)
  default     = ["192.168.1.0/24"] # Covers 192.168.1.0 - 192.168.1.255
}

#Allow all ips for now but change to secure
variable "development_ip" {
  description = "Developer IP"
  type        = string
  default     = "0.0.0.0"
}

variable "vercel_ip" {
  description = "Vercel IP"
  type        = string
  default     = "0.0.0.0"
}
