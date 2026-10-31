#!/usr/bin/env bash
# Update only the approved existing app; this path never creates cloud resources.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${AZURE_CONTEXT_FILE:?Set the private verified lab context}"
: "${APP_NAME:?Set the approved existing App Service name}"
python3 scripts/verify_training_context.py
python3 - <<'PY'
import json, os
from pathlib import Path
context = json.loads(Path(os.environ['AZURE_CONTEXT_FILE']).read_text(encoding='utf-8'))
if os.environ['APP_NAME'] != context.get('app_service_name'):
    raise SystemExit('App name differs from the independently approved private target')
PY
for policy in scm ftp; do
  allowed="$(az resource show --resource-group "$AZURE_RESOURCE_GROUP" --name "$policy" \
    --namespace Microsoft.Web --resource-type basicPublishingCredentialsPolicies \
    --parent "sites/$APP_NAME" --query properties.allow --output tsv)"
  [[ "$allowed" == false ]] || { echo 'Basic publishing authentication must remain disabled'; exit 2; }
done
# Require the deployment result from Kudu; check the live application below.
# Linux startup tracking can lag behind the actual running instance in this lab.
az webapp deploy --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --src-path dist/app.zip --type zip --track-status false --output none
app_host="$(az webapp show --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --query defaultHostName --output tsv)"
python3 - "$app_host" <<'PY'
import json
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

deadline = time.monotonic() + 180
health_url = "https://" + sys.argv[1] + "/health"
while time.monotonic() < deadline:
    try:
        remaining = max(1, deadline - time.monotonic())
        with urlopen(health_url, timeout=min(15, remaining)) as response:
            health = json.load(response)
        if isinstance(health, dict) and health.get("status") == "ready":
            print("Application health ready")
            break
    except (URLError, TimeoutError, ValueError):
        pass
    remaining = deadline - time.monotonic()
    if remaining > 0:
        print("Waiting for application health readiness", flush=True)
        time.sleep(min(5, remaining))
else:
    raise SystemExit("Application did not become ready within 180 seconds")
PY
python3 scripts/predict.py "https://${app_host}"
