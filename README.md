# Building a CI/CD Pipeline

This project delivers a Flask housing-prediction API through GitHub Actions continuous integration and Azure Pipelines continuous delivery to Linux Azure App Service. The repository includes actual application tests, source packaging, a Cloud Shell command sequence, and a project plan.

**Current state:** local implementation, validation, the first hosted GitHub Actions build, and the populated Trello board are complete. Azure Cloud Shell, App Service deployment, Azure Pipelines delivery, final cloud evidence, and the demonstration video remain to be completed. The successful GitHub build is not proof of an Azure App Service deployment.

The latest local suite passes 48 tests, including seventeen cases for binding deployment
to the exact verified training context, with pylint 10/10. A genuine read-only
check against the dedicated Project 2 lab also passed. See the
[guard validation record](evidence/training-context-guard.txt); it records no cloud
deployment.

Source repository: https://github.com/djessijorge9-ship-it/nd082-azure-cicd

[![Python continuous integration](https://github.com/djessijorge9-ship-it/nd082-azure-cicd/actions/workflows/ci.yml/badge.svg)](https://github.com/djessijorge9-ship-it/nd082-azure-cicd/actions/workflows/ci.yml)

The badge reports the actual repository status. The [first real push-triggered run](https://github.com/djessijorge9-ship-it/nd082-azure-cicd/actions/runs/40173810937), for commit `49ec5e503c7ba5e65db020fb277571e4ebd9f902`, completed successfully on 25 October 2026 in 50 seconds. On the Linux hosted runner, all 31 tests passed and pylint scored 10/10. Test results and the deployment-source archive were published as artifacts.

![Successful hosted GitHub Actions run](evidence/github-actions-run.png)

![Passing badge in the actual repository README](evidence/github-actions-badge.png)

## Architecture

![Application and delivery architecture](docs/architecture.svg)

Each commit to `main` or `master` triggers the GitHub lint/test/package workflow. The prepared Azure Pipeline is designed to trigger on those commits once connected in Azure DevOps. Pull requests run build validation; the deployment stage excludes pull requests. The Azure Pipeline is configured to publish JUnit results and deploy the tested source archive. Its Azure Resource Manager connection and App Service name must be configured as persistent pipeline variables, outside source code. Cloud Shell supplies the initial build/deployment and prediction/log checks.

## Project plan

The [original and revised project plan](docs/Project-Plan.xlsx) contains weekly deliverables and task estimates, the current status of each task, and annual/quarterly milestones. Its revised plan remains open until the cloud evidence has been collected. Estimates are planning assumptions, not claims about actual labour time. The [CSV task list](docs/PROJECT_PLAN.csv) offers a plain-text companion.

- [Trello board](https://trello.com/b/9wbc68TD/nd082-azure-ci-cd): publicly readable board with To Do, In Progress and Done lists and cards T1–T8 matching the workbook. Only board members can edit. T1, T2 and T4 are Done; cloud deployment and final demonstration tasks remain To Do.
- Native spreadsheet link: not yet published. The modern Excel workbook is included in this repository; the rubric also permits a spreadsheet link or a `.xls` file.

![Populated project board after CI verification](evidence/trello-board.png)

## Run locally

Use Python 3.12 and a virtual environment. From the repository root on Bash:

```bash
python3 -m venv .venv
source .venv/bin/activate
make all
make test
make run
```

On Windows, activate `.venv\Scripts\Activate.ps1`. GNU Make is optional for local checks: run `python -m pip install -r requirements-dev.txt`, `python -m pylint app.py scripts tests`, `python -m pytest -v`, and `python scripts/package_app.py` directly.

In another terminal:

```bash
python scripts/predict.py http://127.0.0.1:5000
```

For the included sample, the expected prediction is approximately `30.2110938017682`. The response also contains a unique request ID. `GET /health` reports whether the model loaded. The service rejects missing/extra features, invalid JSON, non-finite values, mismatched batches, requests larger than 16 KiB, and batches larger than 100 rows. It logs prediction values and request IDs without logging all input features.

### Model contract and compatibility

The model uses exactly `CHAS, RM, TAX, PTRATIO, B, LSTAT` in that order. The starter's selected LinearRegression was trained on raw features, so the service does not fit a scaler on inference data. The original starter app did fit one on every request, which made a single-row request an all-zero vector. This correction changes the obsolete example prediction shown in the original README.

The supplied serialized model was created with scikit-learn 1.1.3, while the current starter pins 1.5.1. Instead of suppressing that compatibility warning, `scripts/train_model.py` reproduces the official notebook's six-feature split and training process using the included CSV, seed 7, and scikit-learn 1.5.1. Training uses 404 rows and testing uses 102 rows. Actual held-out MSE is `39.95883743552935`; this is a reproducibility result, not a claim of a production-quality model. Feature order, coefficients, versions, and dataset/model hashes are in `Housing_price_model/metadata.json`.

The historical Boston dataset contains a racially constructed feature. It is retained only to reproduce the supplied educational deployment exercise and is unsuitable for real housing decisions. A new application should use an appropriate dataset and a versioned training/preprocessing pipeline.

## Azure Cloud Shell and delivery

The [cloud runbook](docs/CLOUD_RUNBOOK.md) details the full sequence. Use only the verified Project 2 training identity and its exact existing `Azuredevops` resource group, whose metadata location is `eastus`. App Service targets `eastus2` by default, with `centralus` and `northeurope` as lab-permitted alternatives. The Bash file [commands.sh](commands.sh) includes the required `az webapp up -n "$APP_NAME"` operation, the build/tests, HTTPS configuration, prediction, and log setup. Before any deployment, a read-only guard compares the active username hash, tenant, subscription and exact single resource group with an independently verified private context file, then checks the separate App Service region. Keep that context file outside the repository and evidence archive.

The scripts explicitly disable SCM and FTP basic publishing authentication.
Deploy with current Azure CLI using Microsoft Entra authentication, or the
prepared AzureWebApp pipeline task with an authorized connection; do not enable
basic authentication or create publishing passwords as a workaround.

Creating the approved Azure DevOps organization added one service-managed billing
resource group. The private context records only that exact auxiliary group's
ID/name/location as read-only metadata. The guard rejects unknown or changed
groups; deployment and cleanup still target only `Azuredevops`.

```bash
export AZURE_CONTEXT_FILE='/private/location/project02-approved-context.json'
export AZURE_RESOURCE_GROUP='Azuredevops'
export AZURE_LOCATION='eastus2'
export APP_NAME='the-approved-unique-app-name'
bash commands.sh
export APP_URL="https://${APP_NAME}.azurewebsites.net"
bash make_predict_azure_app.sh
az webapp log tail --resource-group "$AZURE_RESOURCE_GROUP" --name "$APP_NAME"
```

Set the Azure DevOps pipeline variables `azureServiceConnection` and `webAppName` to permitted existing values. The training rules prohibit creating an Azure AD application/service principal. Stop if a permitted service connection or runner cannot be used; do not substitute a GitHub workflow for the required Azure Pipelines demonstration.

The deployment archive is `dist/app.zip`, with only the runtime files at its root. `startup.txt` uses Gunicorn, access/error logs to stdout, two workers, and port 8000. Flask debug mode is disabled. Python 3.12 must be supported by the selected App Service runtime.

## Validation and evidence

Local validation records and hosted GitHub CI evidence are stored under `evidence/` with their scope clearly labelled. Current rubric evidence:

| Required evidence | Status |
| --- | --- |
| Project cloned into Azure Cloud Shell | Pending actual Cloud Shell run |
| Passing `make all` and separate test output in Cloud Shell | Pending actual Cloud Shell run |
| GitHub Actions successful build and badge screenshot | Verified successful run 40173810937; screenshots above |
| App Service overview and running application | Pending Azure deployment |
| Azure Pipelines successful test and deployment screenshots | Pending real pipeline run |
| Prediction JSON in Azure Cloud Shell | Pending deployed prediction |
| Prediction value in streamed application logs | Pending actual log stream |
| Complete Trello board and final project plan | Board populated; final plan awaits cloud results |
| Clear narrated 1080p demonstration, 1–5 minutes | Pending actual workflow recording |

`evidence/status.json` records the current observed state; its empty URLs do not imply completed remote work. No screenshot has been fabricated or repurposed from a local environment as cloud evidence.

## Enhancements

Replace the legacy training dataset, include model/data drift checks and model version headers, add approved staging/rollback, pin dependency updates through automated review, and monitor availability and latency. These are future improvements, not completed work or authorization for ongoing Azure spend.

## Demo

YouTube screencast: not yet recorded or published. It must show Cloud Shell login and build, GitHub Actions, Azure Pipelines deployment, and a successful deployed JSON prediction, with readable text and clear audio.

## Sources and attribution

- [Official Udacity starter](https://github.com/udacity/nd082-Azure-Cloud-DevOps-Starter-Code), commit `a239a572c6d6153317f29841973b49a9f78a84f9`. The included CSV and model training approach derive from `C2-AgileDevelopmentwithAzure/project/starter_files/flask-sklearn`. Original source is preserved separately for comparison. Its license is included as `LICENSE.udacity.md`.
- [Azure Pipelines Python App Service tutorial](https://learn.microsoft.com/en-us/azure/devops/pipelines/ecosystems/python-webapp?view=azure-devops), checked 25 October 2026.
- [Azure App Service Python deployment guide](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python), checked 25 October 2026.
- Current classroom project rubric, ND082 version 3.0.16, Building a CI/CD Pipeline, checked 25 October 2026.
