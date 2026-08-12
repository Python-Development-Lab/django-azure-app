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

variable "cost_export_identity_principal_id" {
  type        = string
  default     = ""
  description = "Principal ID of the Cost Management Export System-Assigned Identity. Empty until the export is created via docs/cost-export-setup.md, then set and re-apply."
}

variable "human_admin_object_id" {
  type        = string
  description = "Optional: Object ID of a human operator who should retain independent Key Vault Administrator access (e.g. project owner). Leave empty (default) to skip."
  default     = ""
}

# Entra External ID (CIAM) settings. These existed as manually-created
# app settings on the live App Service (added outside Terraform, likely
# via Portal/CLI during initial CIAM setup) and were NOT present in this
# configuration. Discovered 10.08.2026 via `terraform plan` showing them
# as pending deletion (Terraform's app_settings map replaces the whole
# map, so anything set out-of-band gets silently dropped on next apply).
# Backfilled here with current live values so this apply is a pure
# addition (COST_EXPORT_* wiring) with zero drift on these five settings.
variable "external_id_client_id" {
  type        = string
  sensitive   = true
  description = "Entra External ID (CIAM) app client ID"
}

variable "external_id_client_secret" {
  type        = string
  sensitive   = true
  description = "Entra External ID (CIAM) app client secret"
}

variable "external_id_tenant_id" {
  type        = string
  sensitive   = true
  description = "Entra External ID (CIAM) tenant ID -- distinct from the main var.tenant_id (SECLAB tenant)"
}

variable "external_id_user_flow" {
  type        = string
  default     = "B2X_1_SignUpSignIn"
  description = "Entra External ID (CIAM) user flow name"
}

variable "external_id_redirect_uri" {
  type        = string
  description = "Entra External ID (CIAM) OAuth2 redirect URI"
}
