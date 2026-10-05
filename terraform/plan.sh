#!/bin/bash

set -e

echo "Running terraform plan using the HEAD of main..."

TF_VAR_container_tag=$(git rev-parse origin/main) \
terraform plan \
  -var-file="./env/$(terraform workspace show).tfvars"
