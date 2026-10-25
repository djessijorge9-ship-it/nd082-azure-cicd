# Existing-user hosted CI/CD variant

`azure-pipelines-existing-user.yml` runs the full tests, packaging, deployment and
prediction smoke test in one bounded Ubuntu 24.04 Microsoft-hosted job. The
original `azure-pipelines.yml` is retained for environments with an authorized
Azure Resource Manager service connection. The original definition is disabled
while no such connection exists; a configured YAML file alone is not deployment
evidence.

The separate five-minute `azure-pipelines-probe.yml` is CI only. Its successful
actual run established that the organization has working Microsoft-hosted
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

This is a manual authentication bootstrap for each fresh hosted run. Commits
trigger the pipeline, but it is not fully unattended delivery: the default opt-in
prevents a new run from silently obtaining authentication. Record that limitation
with the actual run evidence.

The Azure CLI profile and decoded context live only under the job's temporary
directory. An `always()` cleanup task removes them after the job, and the hosted
worker is discarded by Azure Pipelines. Checkout does not persist repository
credentials. Only the tested public runtime archive is published as an artifact.

The deployment script updates an existing app only, checks its private approved
name and refuses to proceed unless SCM and FTP basic publishing authentication
remain disabled. Current Azure CLI uses Microsoft Entra authentication for
deployment; no new service principal, role assignment, service connection, PAT,
agent registration or extra VM is required by this variant.

Azure Pipelines uses commits in the private Azure Repos repository. Importing a
public GitHub snapshot does not establish a GitHub synchronization webhook.
Record the actual Azure source commit and corresponding public source snapshot
when updating the mirror, then retain the actual successful full-job run URL.
