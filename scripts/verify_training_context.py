"""Refuse deployment unless the active CLI identity matches the verified lab.

The approved context is private, outside this repository. No token is requested
or written by this check, and it performs only read operations.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


class ContextError(ValueError):
    """A deployment target is not the exact verified Project 2 training context."""


def verify_context(expected, account, groups, resource_group, location):
    """Validate identity, subscription and the single assigned group before writes."""
    expected_groups = expected.get("groups", [])
    if not expected.get("identity_matches_current_lab") or len(expected_groups) != 1:
        raise ContextError("An independently verified single-group lab context is required")
    approved_group = expected_groups[0]
    if (approved_group.get("name") != "Azuredevops"
            or approved_group.get("location") not in ("eastus", "southcentralus")):
        raise ContextError("Approved context is not the current Project 2 lab")
    if resource_group != "Azuredevops":
        raise ContextError("Refusing a group outside the exact approved lab")
    if location not in ("eastus2", "centralus", "northeurope"):
        raise ContextError("App Service region must follow the lab's permitted deployment regions")
    username = account.get("user", {}).get("name", "")
    username_hash = hashlib.sha256(username.lower().encode()).hexdigest()
    if username_hash != expected.get("username_sha256"):
        raise ContextError("Active CLI identity differs from the verified training identity")
    if account.get("tenantId") != expected.get("tenant_id"):
        raise ContextError("Active tenant differs from the verified training tenant")
    if account.get("id") != expected.get("subscription_id"):
        raise ContextError("Active subscription differs from the verified training subscription")
    # Organization billing may add one separately approved read-only metadata
    # group. Match every ID/name/location exactly; no prefix allowlist is used.
    auxiliary = expected.get("read_only_auxiliary_groups", [])
    if len(auxiliary) > 1:
        raise ContextError("At most one independently approved billing metadata group is permitted")
    baseline = [approved_group, *auxiliary]
    if len(groups) != len(baseline):
        raise ContextError("Resource groups differ from the independently verified exact baseline")
    references = {group["id"]: group for group in baseline}
    if len(references) != len(baseline):
        raise ContextError("Approved group IDs must be unique")
    for group in groups:
        reference = references.get(group.get("id"))
        if reference is None or any(group.get(key) != reference.get(key)
                                    for key in ("id", "name", "location")):
            raise ContextError("An unknown or changed resource group is present")
    actual = next(group for group in groups if group["id"] == approved_group["id"])
    return {"verified": True, "resource_group": resource_group,
            "resource_group_location": actual["location"], "app_service_location": location}


def cli_json(*args):
    """Read Azure CLI JSON without exposing account or credential output."""
    executable = shutil.which("az")
    if not executable:
        raise ContextError("Install the official Azure CLI and add it to PATH")
    result = subprocess.run([executable, *args, "--output", "json"], check=False,
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise ContextError("Azure CLI context read failed; no deployment was attempted")
    return json.loads(result.stdout)


def main():
    """Check explicit private context before a shell script can provision resources."""
    context_path = os.environ.get("AZURE_CONTEXT_FILE")
    if not context_path:
        raise ContextError("Set AZURE_CONTEXT_FILE to the private verified lab context")
    expected = json.loads(Path(context_path).read_text(encoding="utf-8"))
    result = verify_context(expected, cli_json("account", "show"), cli_json("group", "list"),
                            os.environ.get("AZURE_RESOURCE_GROUP"),
                            os.environ.get("AZURE_LOCATION"))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
