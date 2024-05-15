#!/usr/bin/env bash
set -eu

# initialize pre-commit

git config --global --add safe.directory /home/calitp/app
pre-commit install --overwrite
