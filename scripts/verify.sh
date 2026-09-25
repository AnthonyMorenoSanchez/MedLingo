#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
make lint
make test
make ingest-offline
(cd backend && ../.venv/bin/python -m ingest.report --check)
make build
make e2e
.venv/bin/python scripts/check_budget.py
echo 'VERIFY OK'
