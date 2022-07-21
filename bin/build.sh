#!/usr/bin/env bash
set -eu

docker compose build client

docker compose build dev
