#!/usr/bin/env bash

set -e

uv run celery \
    -A app.celery_app:celery_app \
    worker \
    --hostname=control@%h \
    --queues=control \
    --concurrency=1 \
    --pool=solo \
    --loglevel=info