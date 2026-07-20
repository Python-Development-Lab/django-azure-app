variable "environment" {
  type        = string
  default     = "staging"
  description = "Deployment environment"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be staging or production."
  }
}

variable "location" {
  type        = string
  default     = "westeurope"
  description = "Azure region"
}

variable "project_name" {
  type        = string
  default     = "django-azure"
  description = "Project name prefix for all resources"
}

variable "owner_email" {
  type        = string
  description = "Owner email for tags"
}

variable "tenant_id" {
  type        = string
  sensitive   = true
  description = "Azure AD tenant ID"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "PostgreSQL admin password"
}

variable "django_secret_key" {
  type        = string
  sensitive   = true
  description = "Django SECRET_KEY"
}

variable "azure_client_id" {
  type        = string
  sensitive   = true
  description = "Entra ID App client ID"
}

variable "azure_client_secret" {
  type        = string
  sensitive   = true
  description = "Entra ID App client secret"
}

variable "azure_redirect_uri" {
  type        = string
  description = "OAuth2 redirect URI"
}

variable "terraform_object_id" {
  type        = string
  description = "Object ID of the user/SP running Terraform (Key Vault access)"
}

variable "human_admin_object_id" {
  type        = string
  description = "Optional: Object ID of a human operator who should retain independent Key Vault Administrator access (e.g. project owner). Leave empty (default) to skip."
  default     = ""
}
