variable "prefix" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "app_subnet_id" {
  type = string
}

variable "key_vault_id" {
  type = string
}

variable "key_vault_uri" {
  type = string
}

variable "db_host" {
  type = string
}

variable "db_name" {
  type = string
}

variable "db_user" {
  type    = string
  default = "djangoadmin"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "azure_client_id" {
  type      = string
  sensitive = true
}

variable "azure_client_secret" {
  type      = string
  sensitive = true
}

variable "azure_tenant_id" {
  type      = string
  sensitive = true
}

variable "django_secret_key" {
  type      = string
  sensitive = true
}

variable "azure_redirect_uri" {
  type = string
}

variable "cost_export_storage_account_name" {
  type        = string
  default     = ""
  description = "Name of the Cost Management Export storage account (module.cost_export.storage_account_name). Wired as the COST_EXPORT_STORAGE_ACCOUNT app setting so core/services.py can read the daily CSV export. Left optional/empty to avoid a hard dependency ordering requirement -- an empty value reproduces the current silent-skip behavior in _fetch_latest_export_csv()."
}

variable "cost_export_container_name" {
  type        = string
  default     = "cost-exports"
  description = "Name of the blob container holding Cost Management Export CSVs. Matches core/services.py's COST_EXPORT_CONTAINER default and module.cost_export's container name."
}

variable "external_id_client_id" {
  type      = string
  sensitive = true
}

variable "external_id_client_secret" {
  type      = string
  sensitive = true
}

variable "external_id_tenant_id" {
  type      = string
  sensitive = true
}

variable "external_id_user_flow" {
  type    = string
  default = "B2X_1_SignUpSignIn"
}

variable "external_id_redirect_uri" {
  type = string
}

variable "tags" {
  type = map(string)
}
