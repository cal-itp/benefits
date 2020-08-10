#!/usr/bin/env bash
set -e

# Build the main app image
docker-compose build --no-cache client && \

# Ensure the local database container is running
docker-compose up -d db && \

# Run Django database migrations
docker-compose run client python manage.py migrate && \

# Load sample Django model data
docker-compose run client python manage.py loaddata EligibilityTypes EligibilityVerifiers TransitAgencies && \

# Create a superuser account for backend admin access
docker-compose run client python manage.py createsuperuser