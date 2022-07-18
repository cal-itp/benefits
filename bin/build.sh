#!/usr/bin/env bash
set -eu

cd .devcontainer/

docker compose build client

docker compose build dev
