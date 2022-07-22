#!/usr/bin/env bash
set -eux

# copy old migrations to temporary directory

cp -r benefits/core/migrations benefits/core/old_migrations

# regenerate

python manage.py makemigrations

# copy over migrations that don't exist

cp benefits/core/old_migrations/* benefits/core/migrations --no-clobber --recursive

# clean up temporary directory
rm -rf benefits/core/old_migrations

# reformat with black

python -m black benefits/core/migrations/0001_initial.py
