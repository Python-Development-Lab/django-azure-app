variable "prefix" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type = string
}

variable "tenant_id" {
  type      = string
  sensitive = true
}

variable "data_subnet_id" {
  type = string
}

variable "kv_dns_zone_id" {
  type = string
}

variable "django_secret_key" {
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

variable "tags" {
  type = map(string)
}

variable "terraform_object_id" {
  description = "Object ID of the user/SP running Terraform (Key Vault Administrator access)"
  type        = string
}

variable "human_admin_object_id" {
  description = "Optional: Object ID of a human operator who should retain Key Vault Administrator access independently of the CI/CD service principal (e.g. for manual debugging via az cli). Leave empty to skip."
  type        = string
  default     = ""
}
