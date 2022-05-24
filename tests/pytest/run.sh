#!/usr/bin/env bash
set -eu

pytest --cov=benefits --cov-branch

# clean out old coverage results
rm -rf benefits/static/coverage
coverage html --directory benefits/static/coverage
