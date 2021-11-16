#!/usr/bin/env bash
set -eu

# initialize hook environments
pre-commit install --install-hooks --overwrite

# manage commit-msg hooks
pre-commit install --hook-type commit-msg

# install cypress
cd tests/e2e && npm install && npx cypress install
