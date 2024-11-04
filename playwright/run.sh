#!/bin/bash

set -e

base_url="https://dev-benefits.calitp.org"

pytest --base-url $base_url --tracing on -v --template=html1/index.html --report=test-results/report.html --video on
