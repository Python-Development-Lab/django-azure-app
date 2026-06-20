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
