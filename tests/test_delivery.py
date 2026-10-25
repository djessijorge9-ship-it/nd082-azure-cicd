from pathlib import Path
from zipfile import ZipFile

import yaml

from scripts import package_app

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
    build, deployment = pipeline["stages"]
    assert build["stage"] == "Build"
    steps = build["jobs"][0]["steps"]
    assert any(step.get("script") == "make all" for step in steps)
    assert any(step.get("task") == "PublishTestResults@2" for step in steps)
    assert deployment["dependsOn"] == "Build"
    assert "PullRequest" in deployment["condition"]
    assert "succeeded()" in deployment["condition"]
    deploy_steps = deployment["jobs"][0]["strategy"]["runOnce"]["deploy"]["steps"]
    assert deploy_steps[0]["checkout"] == "self"
    task = next(step for step in deploy_steps if step.get("task") == "AzureWebApp@1")
    assert task["inputs"]["azureSubscription"] == "$(azureServiceConnection)"
    assert task["inputs"]["appType"] == "webAppLinux"
    assert task["inputs"]["runtimeStack"] == "PYTHON|3.12"


def test_github_workflow_has_real_build_on_push_and_pull_request():
    workflow = yaml.load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"),
                         Loader=yaml.BaseLoader)
    assert set(workflow["on"]) == {"push", "pull_request", "workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert any(step.get("run") == "make all" for step in workflow["jobs"]["build-test"]["steps"])
