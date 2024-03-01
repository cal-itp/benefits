#!/usr/bin/env bash
set -eux

# generate

python manage.py makemigrations

# reformat with black

python -m black benefits/core/migrations/*.py
