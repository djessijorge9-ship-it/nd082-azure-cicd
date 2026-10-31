# Azure Pipelines configuration

`azure-pipelines-existing-user.yml` runs on Microsoft-hosted Ubuntu 24.04 and reads the GitHub repository through its GitHub App connection.

## CI

Push and pull-request events run Python 3.12 installation, lint, tests and runtime packaging through `make all`. JUnit results are published from `test-results/junit.xml` and `dist/app.zip` is published as `app-source`.

## Deployment inputs

| Input | Purpose |
| --- | --- |
| `approvedContextBase64` | Secret variable containing the base64-encoded classroom scope JSON |
| `webAppName` | Existing App Service name from that scope configuration |
| `allowDeviceCodeBootstrap` | Boolean parameter, false by default; true enables device authentication and deployment |

The scope JSON contains the username hash, tenant/subscription IDs, assigned writable group, exact read-only billing group and `app_service_name`. Store its value outside source and artifacts.

## Deployment flow

Authentication and deployment require successful CI, main, a non-PR run and `allowDeviceCodeBootstrap=true`. The Azure CLI device sign-in authenticates the assigned classroom account. The guard then checks the identity, subscription, group IDs/locations and app name.

`scripts/deploy_existing_training_app.sh` updates the existing app using Microsoft Entra authentication and disabled SCM/FTP basic publishing authentication. It uses `--track-status false`, then requires HTTPS `/health` status `ready` within 180 seconds and a successful prediction response.

The Azure profile and decoded context are written to the hosted job's temporary directory. The final `always()` step removes them. Repository credentials are not persisted by checkout.

## Verified execution

For source `d15af0f8f617ea3b6cfaa5cf90b027cb594311b7` on 31 October 2026:

- [Build 3](https://dev.azure.com/nd082-cicd-dj-20261031/ND082-CICD/_build/results?buildId=3) ran automatically from GitHub: 51/51 Passed, one artifact and 56s overall.
- [Build 5](https://dev.azure.com/nd082-cicd-dj-20261031/ND082-CICD/_build/results?buildId=5) completed the deployment flow: 51/51 Passed in 1.600s, zero unreported, one artifact, 3m13s overall and 3m7s job.

The deployment returned `30.211093795690005` with request ID `ed25992d38834124b1de8c54aa58f542` after application health became ready.
