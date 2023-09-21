#!/usr/bin/env bash
set -eu

# run normal pytests
coverage run -m pytest --no-migrations

# clean out old coverage results
rm -rf benefits/static/coverage

coverage html --directory benefits/static/coverage
