variable "resource_group_name" {
  description = "Resource group for the SARIF archive storage account"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
}

variable "cicd_principal_id" {
  description = "Object ID of the CI/CD service principal (django-azure-sp) that uploads SARIF files"
  type        = string
}
