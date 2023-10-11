#!/usr/bin/env bash

if [ $# -ne 2 ]; then
  echo "Usage: $0 <D|T|P> <secret_name>"
  exit 1
fi

env=$1
secret_name=$2

az keyvault secret show --vault-name "KV-CDT-PUB-CALITP-$env-001" --name "$secret_name"
