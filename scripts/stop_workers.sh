#!/usr/bin/env bash

set -e

uv run celery \
  -A app.celery_app:celery_app \
  control shutdown