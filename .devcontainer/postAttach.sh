#!/usr/bin/env bash
set -eu

# initialize pre-commit
pre-commit install --overwrite

# install cypress
cd tests/cypress && npm install && npx cypress install
