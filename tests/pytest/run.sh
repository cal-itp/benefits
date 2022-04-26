#!/usr/bin/env bash
set -eu

pytest --cov=benefits --cov-branch

# clean out old coverage results
rm -rf benefits/static/coverage
coverage html --directory benefits/static/coverage

echo
echo "Launch the app and visit http://localhost:${DJANGO_LOCAL_PORT}/static/coverage/index.html"
