variable "action_group_id" {
  type = string
}

variable "application_insights" {
  # https://stackoverflow.com/a/57963406
  type = object({
    id                  = string
    location            = string
    resource_group_name = string
  })
  description = "Pass the full azurerm_application_insights resource"
}

variable "name" {
  type        = string
  description = "What to call the ping test"
}

variable "severity" {
  type        = number
  default     = 1
  description = "https://docs.microsoft.com/en-us/azure/azure-monitor/best-practices-alerts#alert-severity"
}

variable "url" {
  type = string
}
