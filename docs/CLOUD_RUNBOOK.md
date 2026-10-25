# Cloud execution runbook

These are executable preparation instructions, not a record of completed Azure work.
Use only the verified Project 2 Udacity training identity and its exact existing
`Azuredevops` resource group, whose metadata location is `eastus`. This live
assignment differs from the older course introduction's `cloud-demo-*` prefix.
The group's metadata location does not determine where App Service is deployed:
use the lab-recommended target `eastus2` by default; `centralus` and `northeurope`
are permitted alternatives. Do not create a resource group, Azure AD application, service
principal, or role assignment in that shared subscription. Do not use a personal
Azure subscription to bypass training limits.

## Required inputs

- Existing source repository URL and authorized GitHub / Azure DevOps connection.
- The private `project02-approved-context.json` captured by independent read-only
  lab discovery, transferred privately to the execution environment. It contains
  the verified username hash, tenant, subscription and exact single resource
  group. Keep this file outside the repository and evidence archive.
  After the approved DevOps organization creation, it also records the exact
  automatically created billing group as read-only baseline metadata. The guard
  does not permit any deployment, modification or cleanup in that auxiliary group;
  arbitrary groups, including other groups with a similar prefix, are refused.
- The exact existing training resource group `Azuredevops` (metadata in `eastus`),
  an App Service target region (`eastus2` by default), and an approved globally
  unique App Service name.
- A permitted existing Azure Resource Manager service connection scoped to the
  training resource group. Automatic workload identity setup still creates an
  application registration: do not use it when lab rules prohibit that action.
- Azure DevOps hosted-runner capacity or an authorized existing self-hosted agent.
- Current official Azure CLI (the verified local version is 2.87.0), with Microsoft
  Entra authentication. The prepared creation commands explicitly disable SCM
  and FTP basic publishing authentication; do not enable it or obtain publishing
  passwords to bypass deployment failures. Use Entra/OAuth-supported CLI or the
  AzureWebApp task with an authorized existing service connection.

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

Capture the clone output and the two genuine test outputs. Bind the active CLI
session to the independently verified private context before provisioning:

```bash
export AZURE_CONTEXT_FILE='/private/location/project02-approved-context.json'
export AZURE_RESOURCE_GROUP='Azuredevops'
export AZURE_LOCATION='eastus2' # App Service target, not the group's metadata location
python3 scripts/verify_training_context.py
az webapp list-runtimes --os-type linux --runtime python --output table
```

Use the approved region and free F1 plan if supported by the training subscription.
If F1 is not supported, stop and obtain a permitted training-tier decision; do not
silently fall back to a paid personal plan. The script `commands.sh`
requires explicit environment inputs and creates resources only in that group.
Both creation paths pass `--basic-auth Disabled`. Confirm the `scm` and `ftp`
basic-publishing policies remain false before collecting final deployment evidence.

```bash
export APP_NAME='the-approved-unique-name'
bash commands.sh
export APP_URL="https://${APP_NAME}.azurewebsites.net"
bash make_predict_azure_app.sh
az webapp log config --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME" \
  --docker-container-logging filesystem
az webapp log tail --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME"
```

The model's expected prediction is approximately `30.2110938017682` for the sample. This
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
