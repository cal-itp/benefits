#!/bin/bash

set -e

if [[ $(terraform workspace show) != "dev" ]]; then
  echo "Running terraform apply against environments other than dev is not supported"
  exit 1
fi

echo "Running terraform apply using an interactively supplied SHA..."

terraform apply \
  -var-file="./env/$(terraform workspace show).tfvars"
