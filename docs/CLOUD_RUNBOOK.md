# Cloud execution runbook

These are reproducible execution instructions. Actual completed runs and their
source snapshots are recorded separately in README and evidence/status.json.
Use only the verified Project 2 Udacity training identity and its exact existing
`Azuredevops` resource group, whose metadata location is `eastus`. This live
assignment differs from the older course introduction's `cloud-demo-*` prefix.
The group's metadata location does not determine where App Service is deployed:
use the lab-recommended target `eastus2` by default; `centralus` and `northeurope`
are permitted alternatives. Do not create a resource group, Azure AD application, service
principal, or role assignment in that shared subscription. Do not use a personal
Azure subscription to bypass training limits.

## Required inputs

- Existing source repository URL and access to the approved Azure DevOps project.
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
- Working free Azure DevOps hosted-runner capacity, as established by the actual
  capacity probe. The verified route uses the existing training user with an
  attended device login; no Azure Resource Manager service connection is needed.
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
export APP_URL="https://$(az webapp show --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME" --query defaultHostName --output tsv)"
bash make_predict_azure_app.sh
az webapp log config --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME" \
  --docker-container-logging filesystem
az webapp log tail --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME"
```

The model's expected prediction is approximately `30.211093795690005` for the sample. This
differs from the old README example because the starter fitted an inference-time
scaler even though its selected linear model was trained on raw values. An actual
prediction and matching request ID must appear in the app's log stream.

## Continuous integration and attended delivery

1. Push the prepared project to the authorized repository. Record the source
   commit and successful GitHub Actions run. Its `make all` includes real tests.
2. Mirror a reviewed public snapshot into the private Azure Repos repository.
   Record both source commit IDs; the mirror is an explicit operation, not a
   GitHub synchronization webhook.
3. Configure `azure-pipelines-existing-user.yml` with the verified context as the
   secret `approvedContextBase64` variable and the existing `webAppName`. Keep
   these values outside source. Explicitly queue a run with
   `allowDeviceCodeBootstrap=true` only after authentication is authorized.
4. Complete Microsoft's device login as the exact provided training user. The
   private guard must pass before deployment. Inspect full tests, actual published
   cases, artifact, Entra deployment, live prediction and token-cache removal.
   Record that this is attended delivery; do not label it unattended automation.
5. Capture App Service and the deployed homepage; retain genuine screenshots of
   the green deployment stage and app prediction. Store redacted copies only.

Full hosted run 3 completed these steps successfully. The original
`azure-pipelines.yml` service-connection alternative is retained but its
unconfigured definition 1 is disabled. Do not enable it unless a separately
authorized existing connection is available. Do not create an Entra application,
service principal, role, PAT or agent VM to bypass the training constraints.

The full pipeline's exact JUnit path fails on missing files or publication errors.
If Build Summary shows no tests/artifacts, read the official Test Runs/Results and
Build Artifacts APIs before drawing a conclusion: run 3 had 48 actual passing
case records and one app-source PipelineArtifact despite that UI discrepancy.

## Evidence and shutdown

Update `evidence/status.json`, `docs/PROJECT_PLAN.csv`, and README with actual
observed results, links, and screenshots. Add the Trello board, shared project-plan
spreadsheet, and screencast links only after those artifacts exist. Run any load
test solely against the authorized training app. Remove only resources created
for this project after evidence is saved; never delete the shared resource group.
