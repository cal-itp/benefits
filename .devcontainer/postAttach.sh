#!/usr/bin/env bash
set -eu

echo [initialize hook environments]
pre-commit install --install-hooks --overwrite

echo [manage commit-msg hooks]
pre-commit install --hook-type commit-msg

echo [install npm packages for app]
npm ci
mkdir -p benefits/static/js
cp node_modules/oidc-client-ts/dist/browser/oidc-client-ts* benefits/static/js

echo [install npm packages for tests]
cd tests/cypress
npm ci
npx cypress install
