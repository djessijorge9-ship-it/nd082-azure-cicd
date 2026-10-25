#!/usr/bin/env bash
# Run explicitly in the authorized Udacity training session, never as a CI side effect.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${AZURE_CONTEXT_FILE:?Set the private verified Project 2 lab context JSON}"
: "${AZURE_RESOURCE_GROUP:?Use the existing Udacity Azuredevops resource group}"
export AZURE_LOCATION="${AZURE_LOCATION:-eastus2}"
: "${APP_NAME:?Choose an approved globally unique App Service name}"
python3 scripts/verify_training_context.py
python scripts/package_app.py
az appservice plan create --name "${APP_NAME}-plan" --resource-group "$AZURE_RESOURCE_GROUP" \
  --location "$AZURE_LOCATION" --is-linux --sku F1 --tags Project=ND082-CICD
az webapp create --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --plan "${APP_NAME}-plan" --runtime 'PYTHON:3.12' --basic-auth Disabled
az webapp update --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" --https-only true
az webapp config appsettings set --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
az webapp config set --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --startup-file "$(cat startup.txt)"
az webapp deploy --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --src-path dist/app.zip --type zip
app_host="$(az webapp show --name "$APP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" \
  --query defaultHostName --output tsv)"
python scripts/predict.py "https://${app_host}"
