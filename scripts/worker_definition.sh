#!/usr/bin/env bash

set -e

uv run celery \
    -A app.celery_app:celery_app \
    worker \
    --hostname=definition@%h \
    --queues=definition \
    --concurrency=1 \
    --loglevel=info