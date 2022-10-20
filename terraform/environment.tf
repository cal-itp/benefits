locals {
  is_prod    = terraform.workspace == "default"
  env_name   = local.is_prod ? "prod" : terraform.workspace
  env_letter = upper(substr(local.env_name, 0, 1))
}
