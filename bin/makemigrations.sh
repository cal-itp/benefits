#!/usr/bin/env bash
set -eu

# remove existing migration file

rm -f benefits/core/migrations/0001_initial.py

# regenerate

python manage.py makemigrations

# reformat with black

python -m black benefits/core/migrations/0001_initial.py
