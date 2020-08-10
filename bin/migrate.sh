#!/usr/bin/env bash
set -eu

# Run Django database migrations

if [ -z "$DJANGO_ADMIN" ] && [ "$DJANGO_ADMIN" = true ] ; then
    python manage.py migrate admin zero
    python manage.py migrate auth zero
else
    echo "Django not configured for Admin access"
fi

python manage.py migrate core zero
python manage.py migrate