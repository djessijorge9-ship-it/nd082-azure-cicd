#!/usr/bin/env bash
# Prepared Cloud Shell command sequence. Record actual output when it is run.
set -euo pipefail
cd "$(dirname "$0")"
: "${AZURE_CONTEXT_FILE:?Set the private verified Project 2 lab context JSON}"
: "${AZURE_RESOURCE_GROUP:?Set the existing Udacity Azuredevops resource group}"
export AZURE_LOCATION="${AZURE_LOCATION:-eastus2}"
: "${APP_NAME:?Set the approved globally unique App Service name}"
python3 scripts/verify_training_context.py
python3 -m venv .venv
source .venv/bin/activate
make all
make test
# Explicit group and F1 prevent silently selecting a default personal group/tier.
az webapp up -n "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --plan "${APP_NAME}-plan" --location "$AZURE_LOCATION" --sku F1 \
  --runtime 'PYTHON:3.12' --os-type Linux --basic-auth Disabled
az webapp update --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" --https-only true
az webapp config appsettings set --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
az webapp config set --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --startup-file "$(cat startup.txt)"
export APP_URL="https://${APP_NAME}.azurewebsites.net"
bash make_predict_azure_app.sh
az webapp log config --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --docker-container-logging filesystem
# Streaming is intentionally a separate command so this sequence terminates.
printf 'To inspect the live prediction log: az webapp log tail --name %q --resource-group %q\n' \
  "$APP_NAME" "$AZURE_RESOURCE_GROUP"
