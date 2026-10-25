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
az webapp deploy --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --src-path dist/app.zip --type zip --output none
app_host="$(az webapp show --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --query defaultHostName --output tsv)"
python3 scripts/predict.py "https://${app_host}"
