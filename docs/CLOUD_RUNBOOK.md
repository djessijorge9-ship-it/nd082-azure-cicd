# Cloud execution runbook

## Configuration

Use Bash in the supplied Azure Cloud Shell and authenticate to the assigned subscription. The private scope JSON contains the classroom identity hash, tenant, subscription, writable group, read-only billing group and app name. Store it outside the repository.

Set `AZURE_CONTEXT_FILE` to that file. The assigned resource group is `Azuredevops` with metadata location `westeurope`; the App Service target is `eastus2`. The target service is Linux Python 3.12 on F1, named `nd082-dj-cicd-1102-r787`.

## Verified execution - 2 November 2026

The original-heading application was cloned and built in the supplied Cloud Shell: 59 tests passed in 1.74 seconds and `dist/app.zip` was 3,138 bytes. The subsequent homepage-only commit was `722102a0cd6fabf963078a03ac77b7fb27cbe479`.

Its push triggered [GitHub Actions 15](https://github.com/djessijorge9-ship-it/nd082-azure-cicd/actions/runs/41380035852) and [Azure Pipelines 20261102.1](https://dev.azure.com/nd082-cicd-dj-20261102/ND082-CICD/_build/results?buildId=1). GitHub Actions passed 59 tests in 1.58 seconds and packaged the 3,158-byte changed app. Azure's Individual CI run completed Build and Deploy for the same source.

After the changed heading appeared on the live app, a separate Cloud Shell request returned prediction `30.211093795690005` with request ID `17ca1f3a799d4a7dbba3ade30b5ae9b7`. The application log at `2026-11-02T03:21:34.7443324Z` records that ID with `rows=1`; the following `POST /predict` access entry returned HTTP 200. The [README screenshots](../README.md#verified-workflow---2-november-2026) show the clone, tests, change, automatic runs, live page, JSON and matching stream.

## Build

```bash
git clone https://github.com/djessijorge9-ship-it/nd082-azure-cicd.git nd082-cicd
cd nd082-cicd
python3 -m venv .venv
source .venv/bin/activate
make all
```

Use a new directory name if the clone directory already exists. Cloud Shell sessions can reconnect without retaining earlier files; confirm the source directory, active environment and private configuration path in each session.

## Create the application

Set the app name to the value in the private configuration:

```bash
export AZURE_CONTEXT_FILE="$HOME/project02-approved-context-1102-v2.json"
export AZURE_RESOURCE_GROUP=Azuredevops
export AZURE_LOCATION=eastus2
export APP_NAME=nd082-dj-cicd-1102-r787
python3 scripts/verify_training_context.py
python3 -c 'import json,os; assert os.environ["APP_NAME"] == json.load(open(os.environ["AZURE_CONTEXT_FILE"]))["app_service_name"]'
bash commands.sh
```

`commands.sh` runs the build/tests and creates the App Service using `az webapp up -n "$APP_NAME"` with the explicit group, plan, F1 SKU, Python runtime and disabled basic authentication. It configures HTTPS, build automation, startup and logging.

## Configure automatic Azure delivery

1. Connect only this repository through the Azure Pipelines GitHub App and select `azure-pipelines.yml` in [ND082-CICD](https://dev.azure.com/nd082-cicd-dj-20261102/ND082-CICD).
2. Set `azureServiceConnection=nd082-app-wif`, `webAppName=nd082-dj-cicd-1102-r787` and `webAppUrl=https://nd082-dj-cicd-1102-r787.azurewebsites.net`.
3. Authorize this pipeline to use the verified `nd082-app-wif` connection. The associated user-assigned identity `nd082-cicd-1102-deployer` has Website Contributor on the target app.
4. Push the intended source change to main. GitHub Actions runs CI, and Azure Pipelines runs Build followed by Deploy after success. Pull requests run Build.
5. Inspect the automatically triggered runs. Match their source commit to the pushed commit, then inspect tests, the published package, deployment and readiness output.

`AzureWebApp@1` deploys through workload identity federation. The subsequent smoke test requires `/health` status `ready` and the full homepage heading `<h3>Sklearn Prediction Home - Continuous Delivery</h3>` before sending a prediction. Confirm the changed heading in the live HTTPS homepage as well as the deployment logs. SCM and FTP basic publishing authentication remain disabled.

## Predict and stream logs

Start the live stream in one Cloud Shell session:

```bash
export AZURE_RESOURCE_GROUP=Azuredevops
export APP_NAME=nd082-dj-cicd-1102-r787
az webapp log tail --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME"
```

From a second session in the project source directory with its virtual environment active:

```bash
export APP_URL=https://nd082-dj-cicd-1102-r787.azurewebsites.net
python scripts/predict.py "$APP_URL" --wait-for-heading '<h3>Sklearn Prediction Home - Continuous Delivery</h3>'
```

Match the complete `request_id`, prediction value, processed row count and HTTP status in the fresh response and live log. Keep a deployment smoke request separate from this fresh verification request. Use Ctrl+C to stop streaming.

## Cleanup

After the live demonstration and evidence are verified, remove the project-owned App Service, its sole-use F1 plan and deployment identity/role assignment. Verify exact ownership and resource IDs first. Preserve the provided resource group, read-only billing group and any shared resources.

