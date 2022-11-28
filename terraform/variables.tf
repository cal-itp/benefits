# needs to be uppercase "because Azure DevOps will always transform pipeline variables to uppercase environment variables"
# https://gaunacode.com/terraform-input-variables-using-azure-devops

variable "PROD_SERVICE_CONNECTION_APP_ID" {
  description = "Object ID from the Azure DevOps Production service connection/principal application in Active Directory"
  type        = string
}
