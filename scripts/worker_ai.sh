# scripts/worker_ai.sh
set -e

uv run celery \
  -A app.celery_app:celery_app \
  worker \
  --hostname=ai@%h \
  --queues=ai \
  --pool=solo \
  --concurrency=1 \
  --loglevel=info