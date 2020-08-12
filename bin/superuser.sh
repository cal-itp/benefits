#!/usr/bin/env bash
set -e

# Create a superuser account for backend admin access
python manage.py createsuperuser