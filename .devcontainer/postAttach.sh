#!/usr/bin/env bash
set -eu

# initialize hook environments
pre-commit install --install-hooks --overwrite

# manage commit-msg hooks
pre-commit install --hook-type commit-msg

# copy Login.gov client library
cp node_modules/oidc-client-ts/dist/browser/oidc-client-ts* benefits/static/js

# install cypress
cd tests/cypress && npm install && npx cypress install
