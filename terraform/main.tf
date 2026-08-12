terraform {
  required_version = ">= 1.7"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "stdjangotfstate35607"
    container_name       = "tfstate"
    key                  = "staging.terraform.tfstate"
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
  source                = "./modules/key_vault"
  prefix                = local.prefix
  location              = var.location
  resource_group_name   = azurerm_resource_group.main.name
  tenant_id             = var.tenant_id
  data_subnet_id        = module.network.kv_subnet_id
  kv_dns_zone_id        = module.network.kv_dns_zone_id
  django_secret_key     = var.django_secret_key
  azure_client_id       = var.azure_client_id
  azure_client_secret   = var.azure_client_secret
  terraform_object_id   = var.terraform_object_id
  human_admin_object_id = var.human_admin_object_id
  tags                  = local.tags
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
  db_password         = var.db_password
  azure_client_id     = var.azure_client_id
  azure_client_secret = var.azure_client_secret
  azure_tenant_id     = var.tenant_id
  django_secret_key   = var.django_secret_key
  azure_redirect_uri  = var.azure_redirect_uri
  # No cycle: this references module.cost_export's storage_account_name
  # output (depends only on random_string.cost_export_suffix), while
  # module.cost_export's app_reader role assignment separately depends on
  # this module's app_service_principal_id below. At the resource graph
  # level: storage_account -> web_app -> role_assignment is a valid DAG,
  # not a cycle -- Terraform resolves dependencies per-resource, not by
  # textual module declaration order.
  cost_export_storage_account_name = module.cost_export.storage_account_name
  cost_export_container_name       = module.cost_export.container_name
  external_id_client_id            = var.external_id_client_id
  external_id_client_secret        = var.external_id_client_secret
  external_id_tenant_id            = var.external_id_tenant_id
  external_id_user_flow            = var.external_id_user_flow
  external_id_redirect_uri         = var.external_id_redirect_uri
  tags                             = local.tags
}

module "monitoring" {
  source              = "./modules/monitoring"
  prefix              = local.prefix
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  app_service_id      = module.app_service.app_service_id
  subscription_id     = data.azurerm_client_config.current.subscription_id
  tags                = local.tags
}

module "sarif_archive" {
  source              = "./modules/sarif_archive"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  tags                = local.tags
  cicd_principal_id   = var.terraform_object_id
}

module "cost_export" {
  source                            = "./modules/cost_export"
  resource_group_name               = azurerm_resource_group.main.name
  location                          = var.location
  tags                              = local.tags
  app_service_msi_principal_id      = module.app_service.app_service_principal_id
  cost_export_identity_principal_id = var.cost_export_identity_principal_id
}

data "azurerm_client_config" "current" {}
