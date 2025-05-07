#!/bin/bash

set -e

BASE_URL="https://dev-benefits.calitp.org"

pytest --base-url $BASE_URL
