#!/usr/bin/env bash
set -eux

docker compose build --pull client

docker compose build dev

docker compose pull server
