#!/usr/bin/env bash

set -e

cleanup() {
    echo ""
    echo "Stopping VIV..."
    kill 0
}

trap cleanup EXIT INT TERM

./scripts/api.sh &
./scripts/worker_control.sh &
./scripts/worker_frequency.sh &
./scripts/worker_definition.sh &
./scripts/worker_ai.sh &
./scripts/worker_search.sh &

wait