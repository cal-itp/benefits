variable "engineering_group_object_id" {
  description = "Object ID for the Cal-ITP engineering Active Directory Group"
  type        = string
  sensitive   = true
}

variable "container_registry" {
  description = "The name of the container registry"
  type        = string
  default     = "ghcr.io"
}

variable "container_repository" {
  description = "The repository path within the registry."
  type        = string
  default     = "cal-itp/benefits"
}

variable "container_tag" {
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
