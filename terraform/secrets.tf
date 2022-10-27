# https://github.com/cal-itp/benefits-secrets/tree/main/benefits

data "github_repository_file" "dot_env" {
  repository = "benefits-secrets"
  file       = "benefits/${local.env_name}/.env"
}

data "dotenv" "main" {
  string = sensitive(data.github_repository_file.dot_env.content)
}
