# Cloud execution runbook

These are reproducible execution instructions. README records the current
31 October verification; evidence/status.json preserves the 25 October snapshot.
Use only the verified Project 2 Udacity training identity and its exact existing
`Azuredevops` resource group, whose current metadata location is `southcentralus`
(`eastus` in the historical 25 October assignment). This live
assignment differs from the older course introduction's `cloud-demo-*` prefix.
The group's metadata location does not determine where App Service is deployed:
use the lab-recommended target `eastus2` by default; `centralus` and `northeurope`
are permitted alternatives. Do not create a resource group, Azure AD application, service
principal, or role assignment in that shared subscription. Do not use a personal
Azure subscription to bypass training limits.

## Required inputs

- Existing source repository URL and access to the approved Azure DevOps project.
- The current private `project02-approved-context-1031.json` captured by independent read-only
  lab discovery, transferred privately to the execution environment. It contains
  the verified username hash, tenant, subscription and exact single resource
  group. Keep this file outside the repository and evidence archive.
  After the approved DevOps organization creation, it also records the exact
  automatically created billing group as read-only baseline metadata. The guard
  does not permit any deployment, modification or cleanup in that auxiliary group;
  arbitrary groups, including other groups with a similar prefix, are refused.
- The exact existing training resource group `Azuredevops` (current metadata in `southcentralus`),
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
export AZURE_CONTEXT_FILE="$HOME/project02-approved-context-1031.json"
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
python3 -c 'import json,os; assert os.environ["APP_NAME"] == json.load(open(os.environ["AZURE_CONTEXT_FILE"]))["app_service_name"]'
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
2. The verified earlier route mirrored a reviewed snapshot into private Azure
   Repos. The approved repository-scoped GitHub App is now mapped to the existing
   organization/project. Direct GitHub-source definition 2 is configured to
   `azure-pipelines-existing-user.yml` with its private variables saved; GitHub
   Actions run 13 passed for revision `96d91f458890d39bcef866b97a10e44248e6cb6d`.
   Its automatic push-triggered Azure run is not yet verified. Record that actual
   source/run result before treating the integration as complete.
3. Configure `azure-pipelines-existing-user.yml` with the verified context as the
   secret `approvedContextBase64` variable and the existing `webAppName`. Keep
   these values outside source. The revised YAML always runs CI/JUnit/packaging
   before optional authentication. Explicitly queue an attended delivery with
   `allowDeviceCodeBootstrap=true` only after authentication is authorized;
   authentication and deployment also require successful CI, main and a non-PR run.
4. Complete Microsoft's device login as the exact provided training user. The
   private guard must pass before deployment. Inspect full tests, actual published
   cases, artifact, Entra deployment, live prediction and token-cache removal.
   Record that this is attended delivery; do not label it unattended automation.
5. Capture App Service and retain genuine screenshots of the green deployment,
   fresh prediction and streamed application log with its matching request ID.

On 31 October, [earlier full mirror build 2](https://dev.azure.com/nd082-cicd-dj-20261031/ND082-CICD/_build/results?buildId=2)
completed attended delivery successfully for baseline source
`0519833c819252ea70c4e6a36d05d25a37264333`. The Cloud Shell clone and
[GitHub Actions run 12](https://github.com/djessijorge9-ship-it/nd082-azure-cicd/actions/runs/41214014857)
each passed 51 tests. The pipeline ran from 15:22:56 to 15:26:41 UTC and removed
its worker credentials after successful deployment and prediction. This earlier
mirror run does not verify the new direct GitHub-source integration.

`scripts/deploy_existing_training_app.sh` uses `--track-status false` to avoid
the observed Linux startup tracker lag after Kudu completed deployment. It then
requires HTTPS `/health` JSON status `ready` within 180 seconds before the
unchanged fresh prediction check; missing readiness or prediction still fails.

Historical full run 3 belongs to the separate `nd082-dj-20261025` organization.
The original `azure-pipelines.yml` service-connection alternative is retained;
its unconfigured definition 1 was disabled in that historical organization.
Do not enable that alternative unless a separately
authorized existing connection is available. Do not create an Entra application,
service principal, role, PAT or agent VM to bypass the training constraints.

The full pipeline's exact JUnit path fails on missing files or publication errors.
If Build Summary shows no tests/artifacts, read the official Test Runs/Results and
Build Artifacts APIs before drawing a conclusion: run 3 had 48 actual passing
case records and one app-source PipelineArtifact despite that historical UI discrepancy.

## Evidence and shutdown

The latest retained Cloud Shell request at 16:11:01 UTC returned prediction
`30.211093795690005`, request ID `9af7c43087a842b093df42e002c9bf0c`.
The current live-stream screenshot contains the same full ID and value, and the
App Service screenshot shows Running, Healthy runtime, Linux Python 3.12 and F1.
The F1 app is temporarily active for the bounded recording session. The required
replacement human-recorded screencast remains pending; the earlier narrated
screenshot walkthrough is archival. Record the actual operator workflow from
Cloud Shell login through both CI systems, deployment, a fresh JSON response and
streamed logs from the deployed application. The video must be 1–5 minutes,
readable 1080p+ with 16:9 aspect ratio and clear audio. Publish its YouTube link
only after the genuine recording has been checked.

Update dated evidence records and README with actual observed results, links,
and screenshots. The workbook's supplied-template first tab contains the current
31 October plan; its two other tabs preserve the 25 October history. The CSV and
board screenshot remain historical, with original/revised estimates held at 6/7
hours. Keep their old Done statuses distinct from current pending recording and
integration verification. Run any load
test solely against the authorized training app. Remove only resources created
for this project after evidence is saved; never delete the shared resource group.
