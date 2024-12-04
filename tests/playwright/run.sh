#!/bin/bash

set -eux

ENV=$1

if [ $# -ne 1 ]; then
  echo "No environment given... running against local environment"
else
  MARK="-m ${ENV}"
fi

if [ "$ENV" = "dev" ]; then
  BASE_URL="https://dev-benefits.calitp.org"
elif [ "$ENV" = "test" ]; then
  BASE_URL="https://test-benefits.calitp.org"
elif [ "$ENV" = "prod" ]; then
  BASE_URL="https://benefits.calitp.org"
else
  BASE_URL="http://localhost:11369"
  MARK=""
fi

pytest --base-url "$BASE_URL" "$MARK"
