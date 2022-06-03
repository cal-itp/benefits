variable "action_group_id" {
  type = string
}

variable "name" {
  type = string
  description = "What to call the ping test"
}

variable "resource_group_name" {
  type = string
}

variable "severity" {
  type = number
  default = 1
  description = "https://docs.microsoft.com/en-us/azure/azure-monitor/best-practices-alerts#alert-severity"
}

variable "url" {
  type = string
}
