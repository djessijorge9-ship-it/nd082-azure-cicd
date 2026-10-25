"""Prevent writes through stale or unrelated Azure CLI sessions."""
from copy import deepcopy
import hashlib

import pytest

from scripts.verify_training_context import ContextError, verify_context


@pytest.fixture(name="lab")
def verified_lab_context():
    """Use synthetic private identifiers, never real training credentials."""
    group = {"id": "/subscriptions/training-sub/resourceGroups/Azuredevops",
             "name": "Azuredevops", "location": "eastus"}
    expected = {"identity_matches_current_lab": True,
                "username_sha256": hashlib.sha256(b"learner@example.invalid").hexdigest(),
                "tenant_id": "training-tenant", "subscription_id": "training-sub",
                "groups": [group]}
    account = {"user": {"name": "Learner@example.invalid"},
               "tenantId": "training-tenant", "id": "training-sub"}
    return expected, account, [deepcopy(group)]


@pytest.mark.parametrize("app_region", ["eastus2", "centralus", "northeurope"])
def test_exact_verified_group_and_permitted_app_region_are_accepted(lab, app_region):
    result = verify_context(*lab, "Azuredevops", app_region)
    assert result == {"verified": True, "resource_group": "Azuredevops",
                      "resource_group_location": "eastus", "app_service_location": app_region}


@pytest.mark.parametrize("case", ["other_user", "other_tenant", "other_subscription",
                                 "other_group", "extra_group", "wrong_group_id",
                                 "wrong_region", "unverified", "stale_approved_group"])
def test_unapproved_context_is_refused_before_deployment(lab, case):
    expected, account, groups = deepcopy(lab)
    resource_group, location = "Azuredevops", "eastus2"
    if case == "other_user":
        account["user"]["name"] = "unrelated@example.invalid"
    elif case == "other_tenant":
        account["tenantId"] = "unrelated-tenant"
    elif case == "other_subscription":
        account["id"] = "personal-sub"
    elif case == "other_group":
        resource_group = "cloud-demo-old-lab"
    elif case == "extra_group":
        groups.append({"id": "another", "name": "Other", "location": "eastus"})
    elif case == "wrong_group_id":
        groups[0]["id"] = "/subscriptions/another/resourceGroups/Azuredevops"
    elif case == "wrong_region":
        location = "westeurope"
    elif case == "unverified":
        expected["identity_matches_current_lab"] = False
    elif case == "stale_approved_group":
        expected["groups"][0]["name"] = "Azuredevops-other"
    with pytest.raises(ContextError):
        verify_context(expected, account, groups, resource_group, location)
