# many of these are uppercase because Azure DevOps transformed pipeline variables to uppercase environment variables
# https://gaunacode.com/terraform-input-variables-using-azure-devops
# lowercase variables *are* supported when running terraform commands via GH Actions
variable "ENGINEERING_GROUP_OBJECT_ID" {
  description = "Object ID for the Cal-ITP engineering Active Directory Group"
  type        = string
  sensitive   = true
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
  description = "The specific tag of the image to deploy (e.g., a commit SHA)."
}

variable "sp_apply_object_id" {
  description = "Object ID for the GH Actions service principal created by DevSecOps"
  type        = string
  sensitive   = true
}

variable "sp_plan_object_id" {
  description = "Object ID for the plan-only GH Actions service principal created by DevSecOps"
  type        = string
  sensitive   = true
}
