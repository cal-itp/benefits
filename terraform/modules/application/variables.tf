# Terraform Environment
variable "resource_group_name" {
  description = "The name of the resource group for deployment."
  type        = string
}
variable "location" {
  description = "The location of the resource group."
  type        = string
}
variable "env_letter" {
  description = "The single uppercase letter representing the environment (e.g. 'D', 'T', 'P')."
  type        = string
}
variable "env_name" {
  description = "The name of the environment (e.g., 'dev', 'test', 'prod')."
  type        = string
}
variable "is_dev" {
  description = "Indicates if the environment being deployed to is development."
  type        = bool
}
variable "is_prod" {
  description = "Indicates if the environment being deployed to is production."
  type        = bool
}
# Monitoring
variable "log_analytics_workspace_id" {
  description = "The ID of the Log Analytics Workspace for monitoring."
  type        = string
}
# Network
variable "infrastructure_subnet_id" {
  description = "The ID of the 'ACAPP' subnet."
  type        = string
}
# Storage
variable "storage_account_name" {
  description = "The name of the storage account."
  type        = string
}
variable "storage_account_access_key" {
  description = "The primary access key for the storage account."
  type        = string
  sensitive   = true
}
variable "storage_share_name" {
  description = "The name of the File Share for the Django storage directory."
  type        = string
}
# Benefits Container App Image Details
variable "container_registry" {
  description = "The name of the container registry."
  type        = string
}
variable "container_repository" {
  description = "The repository path within the registry."
  type        = string
}
variable "container_tag" {
  description = "The specific tag of the image to deploy."
  type        = string
}
# Key Vault
variable "key_vault_secret_uri_prefix" {
  description = "The base URI for Key Vault secrets (e.g., 'https://myvault.vault.azure.net/secrets')."
  type        = string
}
# App Config
variable "azure_communication_connection_string_name" {
  description = "The connection string name for Azure Communication Services."
  type        = string
}
variable "django_db_password_secret_name" {
  description = "The secret name for the Django database user's password."
  type        = string
}
variable "postgres_admin_password_secret_name" {
  description = "The secret name for the Postgres admin's password."
  type        = string
}
variable "pgadmin_admin_password_secret_name" {
  description = "The secret name for the pgAdmin admin's password."
  type        = string
}
variable "sender_email" {
  description = "The sender email for Azure Communication Services."
  type        = string
}
variable "postgres_fqdn" {
  description = "The FQDN of the PostgreSQL server."
  type        = string
}
variable "postgres_admin_login" {
  description = "The admin username for the postgres database."
  type        = string
}
variable "postgres_admin_db" {
  description = "The name of the postgres database (e.g. 'postgres')."
  type        = string
}
