#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python scripts/predict.py "${1:-http://127.0.0.1:5000}"
