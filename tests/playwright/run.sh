#!/bin/bash

set -e

base_url="https://dev-benefits.calitp.org"

# also uses arguments from pytest.ini
pytest --base-url $base_url
