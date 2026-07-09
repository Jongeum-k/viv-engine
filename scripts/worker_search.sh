# scripts/worker_search.sh

set -e

uv run celery \
  -A app.celery_app:celery_app \
  worker \
  --hostname=search@%h \
  --queues=search \
  --concurrency=1 \
  --pool=solo \
  --loglevel=info