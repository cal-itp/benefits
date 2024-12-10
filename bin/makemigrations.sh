#!/usr/bin/env bash
set -eux

# generate

benefits makemigrations

# reformat with black

python -m black benefits/core/migrations/*.py
