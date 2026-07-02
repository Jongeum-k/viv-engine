#!/usr/bin/env bash

set -e

uv run celery \
    -A app.celery_app:celery_app \
    worker \
    --hostname=frequency@%h \
    --queues=frequency \
    --concurrency=4 \
    --loglevel=info