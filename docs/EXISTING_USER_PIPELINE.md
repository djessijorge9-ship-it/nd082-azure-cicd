# Existing-user hosted CI/CD variant

`azure-pipelines-existing-user.yml` runs CI, test publication and packaging in
one bounded Ubuntu 24.04 Microsoft-hosted job without an Azure login. Azure
authentication, deployment and prediction require an explicit opt-in and a
successful main-branch, non-PR run. The
original `azure-pipelines.yml` is retained for environments with an authorized
Azure Resource Manager service connection. Its unconfigured definition 1 was
disabled in the historical `nd082-dj-20261025` organization; this status refers
to that older organization. A configured YAML file alone is not deployment evidence.

The separate five-minute `azure-pipelines-probe.yml` is CI only. Its successful
historical run established that the old organization had working Microsoft-hosted
capacity; it does not satisfy continuous-delivery evidence.

## Private inputs and approval

- `approvedContextBase64`: secret pipeline variable containing only the verified
  scope JSON, encoded as base64. This includes the username hash, exact tenant and
  subscription, exact writable group, exact approved read-only billing metadata
  and `app_service_name`. It contains no access pass, password or token. Keep its
  value out of source, artifacts and public evidence.
- `webAppName`: the actual approved existing app name.
- `allowDeviceCodeBootstrap`: false by default. Set true only for the specific
  approved hosted run after the account owner authorizes authenticating the
  provided training identity on that temporary Microsoft-hosted worker.

The authentication task displays the standard Microsoft Azure CLI device-code
instructions. An authorized operator opens the official Microsoft page, verifies
the app and signs in as the exact provided lab user. The subsequent guard verifies
the username hash, tenant, subscription, exact group IDs/names/regions and separate
App Service target region before any deployment. It never prints private scope
metadata or tokens. A wrong remembered account fails the guard.

The revised YAML performs CI before the optional login. With the opt-in false,
CI can complete without requesting Azure authentication. With it true, both
authentication and delivery are restricted to successful main-branch, non-PR
runs. Every fresh delivery worker requires the attended training-user login;
this is not unattended Azure deployment.

The Azure CLI profile and decoded context live only under the job's temporary
directory. An `always()` cleanup task removes them after the job, and the hosted
worker is discarded by Azure Pipelines. Checkout does not persist repository
credentials. Only the tested public runtime archive is published as an artifact.

The deployment script updates an existing app only, checks its private approved
name and refuses to proceed unless SCM and FTP basic publishing authentication
remain disabled. Current Azure CLI uses Microsoft Entra authentication for
deployment; no new service principal, role assignment, service connection, PAT,
agent registration or extra VM is required by this variant.

The current approved group's metadata location is `southcentralus`, compared
with `eastus` in the 25 October assignment; the App Service target is `eastus2`.
The private baseline includes only the exact independently approved writable
group and read-only billing group. A previous assignment's context must not be reused.

Deployment uses `--track-status false` because the observed Linux startup tracker
lagged behind the completed Kudu deployment. A separate HTTPS `/health` gate must
report JSON status `ready` within 180 seconds, followed by the unchanged fresh
prediction check. These checks remain failure gates.

The earlier verified build 2 read a reviewed snapshot from private Azure Repos.
That manual mirror did not establish a GitHub synchronization webhook. The
approved GitHub App is now installed for this repository only and mapped to the
existing organization/project. Direct GitHub-source definition 2 is configured
to this YAML, with private scope/app variables saved. GitHub Actions run 13 passed
for revision `96d91f458890d39bcef866b97a10e44248e6cb6d`; an automatic Azure
push-triggered run has not yet been verified. Retain its source and execution result
before claiming that integration is complete.

## Verified full execution

On 31 October 2026, [full mirror build 2](https://dev.azure.com/nd082-cicd-dj-20261031/ND082-CICD/_build/results?buildId=2)
in the current private `ND082-CICD` project succeeded for baseline source
`0519833c819252ea70c4e6a36d05d25a37264333`. It ran from 15:22:56 to 15:26:41 UTC;
all tasks passed, including tests, artifact publication, Entra deployment,
readiness, fresh prediction and removal of worker credentials. Its prediction
was `30.211093795690005`, request ID `a194c0ed5bf14a5f8b69543dbbcaaaa9`.
The corresponding Cloud Shell clone and GitHub Actions run 12 each passed 51 tests.
These results precede the new direct-source integration revision. The required
replacement human YouTube screencast remains pending: 1–5 minutes, readable
1080p+ at 16:9, clear audio, the full login-to-prediction workflow and streamed
logs from the deployed application.

Historical [full run 3](https://dev.azure.com/nd082-dj-20261025/ND082-CICD/_build/results?buildId=3)
completed successfully on 25 October 2026. Azure source
`17bdad0f615507a8d0e68e1585df042dd7918ba9` corresponds to public snapshot
`3fc837af903e12ce98f527539a11848cfe37ae1a`. All steps passed, including
authentication/scope validation, make all, publication, Entra deployment,
deployed prediction and removal of the temporary login cache.

Official APIs independently read back Test Run 3 linked to Build 3, 48 individual
Passed case results, and one app-source PipelineArtifact. The Build Summary UI's
Get started/0 published presentation was inconsistent with those actual records.
See evidence/azure-pipelines-run3-summary.json for the exact observation.
