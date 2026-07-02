#!/usr/bin/env bash

set -e

cleanup() {
    echo ""
    echo "Stopping VIV..."
    kill 0
}

trap cleanup EXIT INT TERM

./scripts/api.sh &
./scripts/worker.sh &

wait