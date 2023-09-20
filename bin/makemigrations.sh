#!/usr/bin/env bash
set -eux

# create temporary directory (if it doesn't already exist)

mkdir -p benefits/core/old_migrations

# move old migrations to temporary directory, but keep init file

mv benefits/core/migrations/* benefits/core/old_migrations
cp benefits/core/old_migrations/__init__.py benefits/core/migrations

# regenerate

python manage.py makemigrations

# copy over migrations that don't exist

cp benefits/core/old_migrations/* benefits/core/migrations --no-clobber --recursive

# clean up temporary directory

rm -rf benefits/core/old_migrations

# reformat with black

python -m black benefits/core/migrations/*.py
