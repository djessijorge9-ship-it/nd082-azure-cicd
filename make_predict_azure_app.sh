#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${APP_URL:?Set APP_URL to the actual HTTPS Azure App Service URL}"
python scripts/predict.py "$APP_URL"
