#!/usr/bin/env bash
set -euo

# Create a superuser account for backend admin access

if [ -z "$DJANGO_ADMIN" ] && [ "$DJANGO_ADMIN" = true ] ; then
    python manage.py createsuperuser
else
    echo "Django not configured for Admin access"
fi