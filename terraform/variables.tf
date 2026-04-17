# needs to be uppercase "because Azure DevOps will always transform pipeline variables to uppercase environment variables"
# https://gaunacode.com/terraform-input-variables-using-azure-devops

variable "ARM_SUBSCRIPTION_ID" {
  description = "Production Subscription ID"
  type        = string
}
variable "DEVSECOPS_OBJECT_ID" {
  description = "Object ID for the DevSecOps principal, which includes the Production service connection"
  type        = string
}

variable "ENGINEERING_GROUP_OBJECT_ID" {
  description = "Object ID for the Cal-ITP engineering Active Directory Group"
  type        = string
}

variable "CONTAINER_REGISTRY" {
  description = "The name of the container registry"
  type        = string
  default     = "ghcr.io"
}

variable "CONTAINER_REPOSITORY" {
  description = "The repository path within the registry."
  type        = string
  default     = "cal-itp/benefits"
}

variable "CONTAINER_TAG" {
  type        = string
  description = "The specific tag of the image to deploy (e.g., 'main')."
}
