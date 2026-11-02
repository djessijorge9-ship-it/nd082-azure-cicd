from io import BytesIO
import json
from pathlib import Path
import shlex
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import yaml

from scripts import package_app
from scripts.predict import wait_for_deployment

ROOT = Path(__file__).resolve().parents[1]


def test_deployment_archive_contains_only_runtime_files():
    package_app.main()
    with ZipFile(ROOT / "dist" / "app.zip") as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(package_app.FILES)
        assert archive.read("app.py") == (ROOT / "app.py").read_bytes()
        assert not any(name.startswith((".venv", ".git", ".env")) for name in archive.namelist())


def test_pipeline_prevents_pull_request_deployment_and_keeps_tests():
    pipeline = yaml.safe_load((ROOT / "azure-pipelines.yml").read_text(encoding="utf-8"))
    assert "main" in pipeline["trigger"]["branches"]["include"]
    assert "main" in pipeline["pr"]["branches"]["include"]
    build, deployment = pipeline["stages"]
    assert build["stage"] == "Build"
    steps = build["jobs"][0]["steps"]
    assert any(step.get("script") == "make all" for step in steps)
    assert any(step.get("task") == "PublishTestResults@2" for step in steps)
    assert deployment["dependsOn"] == "Build"
    assert "ne(variables['Build.Reason'], 'PullRequest')" in deployment["condition"]
    assert "refs/heads/main" in deployment["condition"]
    assert "succeeded()" in deployment["condition"]
    deploy_steps = deployment["jobs"][0]["strategy"]["runOnce"]["deploy"]["steps"]
    assert deploy_steps[0]["checkout"] == "self"
    task = next(step for step in deploy_steps if step.get("task") == "AzureWebApp@1")
    assert task["inputs"]["azureSubscription"] == "$(azureServiceConnection)"
    assert task["inputs"]["appType"] == "webAppLinux"
    assert task["inputs"]["resourceGroupName"] == "Azuredevops"
    assert task["inputs"]["runtimeStack"] == "PYTHON|3.12"
    smoke = next(step for step in deploy_steps
                 if step.get("script", "").startswith("python scripts/predict.py "))
    assert shlex.split(smoke["script"]) == [
        "python", "scripts/predict.py", "$WEB_APP_URL", "--wait-for-heading",
        "<h3>Sklearn Prediction Home - Continuous Delivery</h3>"]
    assert smoke["env"]["WEB_APP_URL"] == "$(webAppUrl)"


def test_github_workflow_has_real_build_on_push_and_pull_request():
    workflow = yaml.load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"),
                         Loader=yaml.BaseLoader)
    assert set(workflow["on"]) == {"push", "pull_request", "workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert any(step.get("run") == "make all" for step in workflow["jobs"]["build-test"]["steps"])


class TestDeploymentReadiness(unittest.TestCase):
    def run_wait(self, health_status, homepage_versions):
        clock = [0.0]
        pages = iter(homepage_versions)
        last_page = homepage_versions[-1]
        requested = []

        def fetch(url, timeout):
            self.assertGreater(timeout, 0)
            requested.append(url)
            if url.endswith("/health"):
                return BytesIO(json.dumps({"status": health_status}).encode())
            self.assertEqual(url, "https://app.example/")
            return BytesIO(next(pages, last_page).encode())

        def advance(seconds):
            clock[0] += seconds

        with patch("scripts.predict.urlopen", side_effect=fetch), \
             patch("scripts.predict.time.monotonic", side_effect=lambda: clock[0]), \
             patch("scripts.predict.time.sleep", side_effect=advance):
            wait_for_deployment("https://app.example", "Release 2", timeout=10)
        return requested

    def test_healthy_old_release_waits_until_changed_release_is_served(self):
        requests = self.run_wait("ready", ["Release 1", "Release 2"])
        self.assertEqual(requests.count("https://app.example/"), 2)

    def test_healthy_old_release_never_satisfies_deployment(self):
        with self.assertRaisesRegex(RuntimeError, "expected ready release"):
            self.run_wait("ready", ["Release 1"])

    def test_changed_release_without_model_readiness_is_refused(self):
        with self.assertRaisesRegex(RuntimeError, "expected ready release"):
            self.run_wait("unavailable", ["Release 2"])
