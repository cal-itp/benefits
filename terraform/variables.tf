# needs to be uppercase "because Azure DevOps will always transform pipeline variables to uppercase environment variables"
# https://gaunacode.com/terraform-input-variables-using-azure-devops

variable "DEVSECOPS_OBJECT_ID" {
  description = "Object ID for the DevSecOps principal, which includes the Production service connection"
  type        = string
}

variable "ENGINEERING_GROUP_OBJECT_ID" {
  description = "Object ID for the Cal-ITP engineering Active Directory Group"
  type        = string
}
