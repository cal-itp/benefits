#!/usr/bin/env bash
set -e

# Load sample Django model data
python manage.py loaddata data/client/*.json