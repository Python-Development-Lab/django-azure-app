terraform {
  required_version = ">= 1.7"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

locals {
  prefix = "${var.project_name}-${var.environment}"
  tags = {
    environment = var.environment
    project     = "django-azure-security-template"
    owner       = var.owner_email
    managed_by  = "terraform"
    cost_center = "portfolio"
  }
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${local.prefix}"
  location = var.location
  tags     = local.tags
}

module "network" {
  source              = "./modules/network"
  prefix              = local.prefix
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

module "key_vault" {
  source              = "./modules/key_vault"
  prefix              = local.prefix
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = var.tenant_id
  data_subnet_id      = module.network.data_subnet_id
  kv_dns_zone_id      = module.network.kv_dns_zone_id
  django_secret_key   = var.django_secret_key
  azure_client_id     = var.azure_client_id
  azure_client_secret = var.azure_client_secret
  tags                = local.tags
}

module "database" {
  source              = "./modules/database"
  prefix              = local.prefix
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  environment         = var.environment
  db_password         = var.db_password
  data_subnet_id      = module.network.data_subnet_id
  pg_dns_zone_id      = module.network.pg_dns_zone_id
  tags                = local.tags
}

module "app_service" {
  source              = "./modules/app_service"
  prefix              = local.prefix
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  environment         = var.environment
  app_subnet_id       = module.network.app_subnet_id
  key_vault_id        = module.key_vault.key_vault_id
  key_vault_uri       = module.key_vault.key_vault_uri
  db_host             = module.database.db_host
  db_name             = module.database.db_name
  tags                = local.tags
}

module "monitoring" {
  source              = "./modules/monitoring"
  prefix              = local.prefix
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  app_service_id      = module.app_service.app_service_id
  tags                = local.tags
}
