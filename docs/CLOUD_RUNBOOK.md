# Cloud execution runbook

## Configuration

Use Bash in the supplied Azure Cloud Shell and authenticate to the assigned subscription. The private scope JSON contains the classroom identity hash, tenant, subscription, writable group, read-only billing group and app name. Store it outside the repository.

Set `AZURE_CONTEXT_FILE` to that file. The assigned resource group is `Azuredevops` with metadata location `southcentralus`; the App Service target is `eastus2`. The target service is Linux Python 3.12 on F1.

## Build

```bash
git clone https://github.com/djessijorge9-ship-it/nd082-azure-cicd.git nd082-cicd
cd nd082-cicd
python3 -m venv .venv
source .venv/bin/activate
make all
```

## Create the application

Set the app name to the value in the private configuration:

```bash
export AZURE_CONTEXT_FILE="$HOME/project02-approved-context-1031.json"
export AZURE_RESOURCE_GROUP=Azuredevops
export AZURE_LOCATION=eastus2
export APP_NAME=nd082-dj-cicd-1031-r779
python3 scripts/verify_training_context.py
python3 -c 'import json,os; assert os.environ["APP_NAME"] == json.load(open(os.environ["AZURE_CONTEXT_FILE"]))["app_service_name"]'
bash commands.sh
```

`commands.sh` runs the build/tests and creates the App Service using `az webapp up -n "$APP_NAME"` with the explicit group, plan, F1 SKU, Python runtime and disabled basic authentication. It configures HTTPS, build automation, startup and logging.

## Configure Azure Pipelines

1. Connect this GitHub repository to Azure Pipelines through the repository-scoped GitHub App.
2. Select `azure-pipelines-existing-user.yml`.
3. Set secret variable `approvedContextBase64` to the base64-encoded scope JSON and `webAppName` to the configured app.
4. Source changes run CI, JUnit publication and packaging. To deploy, run main with `allowDeviceCodeBootstrap=true` and complete the Azure CLI device sign-in.
5. The identity/scope guard must pass before deployment. Authentication and deployment run only after successful CI on main and outside pull requests.

The deployment script uses Entra authentication, waits for completed deployment, requires `/health` JSON status `ready` within 180 seconds and sends a prediction request. SCM and FTP basic publishing authentication remain disabled.

## Predict and stream logs

```bash
export APP_URL="https://$(az webapp show --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME" --query defaultHostName -o tsv)"
bash make_predict_azure_app.sh
az webapp log config --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME" --docker-container-logging filesystem -o none
az webapp log tail --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME"
```

While the stream runs, send another prediction from a second session. Match the complete `request_id` and prediction value in the response and log line. Use Ctrl+C to stop the stream.

## Execution results

On 31 October 2026, source `d15af0f8f617ea3b6cfaa5cf90b027cb594311b7` passed:

- GitHub Actions run 14: 51 tests, 1.27s test time, two artifacts.
- Automatic GitHub-source Azure build 3: 51/51 Passed, 1.816s test time, one artifact.
- Full Azure build 5: 51/51 Passed, 1.600s test time, zero unreported, one artifact and 3m13s overall.

Build 5 completed deployment, readiness and prediction `30.211093795690005` with request `ed25992d38834124b1de8c54aa58f542`. The pipeline removes its job-local Azure profile and private context after execution.
