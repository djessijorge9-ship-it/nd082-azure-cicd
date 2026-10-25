# Cloud execution runbook

These are executable preparation instructions, not a record of completed Azure work.
Use only the Udacity-provided training subscription and existing `cloud-demo-*`
resource group. Do not create a resource group, Azure AD application, service
principal, or role assignment in that shared subscription. Do not use a personal
Azure subscription to bypass training limits.

## Required inputs

- Existing source repository URL and authorized GitHub / Azure DevOps connection.
- Existing training resource group, subscription, permitted region (East US 2,
  Central US, or North Europe), and globally unique App Service name.
- A permitted existing Azure Resource Manager service connection scoped to the
  training resource group. Automatic workload identity setup still creates an
  application registration: do not use it when lab rules prohibit that action.
- Azure DevOps hosted-runner capacity or an authorized existing self-hosted agent.

## Cloud Shell and initial App Service

Choose Bash Cloud Shell, clone the actual project repository and open its root:

```bash
git clone "$REPOSITORY_URL" nd082-cicd
cd nd082-cicd
python3 -m venv .venv
source .venv/bin/activate
make all
make test
```

Capture the clone output and the two genuine test outputs. Inspect the currently
selected subscription and the existing resource group before provisioning:

```bash
az account show --query '{name:name,id:id}' --output table
az group show --name "$AZURE_RESOURCE_GROUP" --query '{name:name,location:location}'
az webapp list-runtimes --os-type linux --runtime python --output table
```

Use the approved region and free F1 plan if supported by the training subscription.
If F1 is not supported, stop and obtain a permitted training-tier decision; do not
silently fall back to a paid personal plan. The script `commands.sh`
requires explicit environment inputs and creates resources only in that group.

```bash
export AZURE_RESOURCE_GROUP='the-existing-training-group'
export AZURE_LOCATION='eastus2'
export APP_NAME='the-approved-unique-name'
bash commands.sh
export APP_URL="https://${APP_NAME}.azurewebsites.net"
bash make_predict_azure_app.sh
az webapp log config --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME" \
  --docker-container-logging filesystem
az webapp log tail --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME"
```

The deployed model predicts approximately `30.2110938017682` for the sample. This
differs from the old README example because the starter fitted an inference-time
scaler even though its selected linear model was trained on raw values. An actual
prediction and matching request ID must appear in the app's log stream.

## Continuous integration and automatic delivery

1. Push the prepared project to the authorized repository. Record the source
   commit and successful GitHub Actions run. Its `make all` includes real tests.
2. Import `azure-pipelines.yml` into the authorized Azure DevOps project.
3. Supply the actual existing resource-manager connection and App Service name as
   persistent pipeline variables `azureServiceConnection` and `webAppName`.
   Authorize only this pipeline to the connection.
4. Run once, inspect test results, artifact, deployment task, and prediction smoke
   test. Then make an innocuous documented source change and commit it so a second
   run demonstrates automatic delivery. Record both run URLs and commits.
5. Capture App Service and the deployed homepage; retain genuine screenshots of
   the green deployment stage and app prediction. Store redacted copies only.

The pipeline has not been validated by merely parsing its YAML locally. If the
training identity cannot access a permitted service connection or hosted agents,
that is a concrete external blocker to document and resolve with Udacity.

## Evidence and shutdown

Update `evidence/status.json`, `docs/PROJECT_PLAN.csv`, and README with actual
observed results, links, and screenshots. Add the Trello board, shared project-plan
spreadsheet, and screencast links only after those artifacts exist. Run any load
test solely against the authorized training app. Remove only resources created
for this project after evidence is saved; never delete the shared resource group.
