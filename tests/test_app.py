import copy
import json
import math
from pathlib import Path

import joblib
import pytest

from app import DEFAULT_MODEL, FEATURES, create_app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client():
    service = create_app()
    service.config.update(TESTING=True)
    return service.test_client()


@pytest.fixture
def payload():
    return json.loads((ROOT / "sample-payload.json").read_text(encoding="utf-8"))


def test_home_and_readiness(client):
    assert client.get("/").status_code == 200
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ready"
    assert response.json["features"] == list(FEATURES)


def test_prediction_matches_independent_linear_formula(client, payload):
    model = joblib.load(DEFAULT_MODEL)
    row = [payload[column]["0"] for column in FEATURES]
    expected = float(model.intercept_ + sum(c * value for c, value in zip(model.coef_, row)))
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json["prediction"] == pytest.approx([expected])
    assert len(response.json["request_id"]) == 32
    assert math.isfinite(response.json["prediction"][0])


def test_batch_invariance_and_input_sensitivity(client, payload):
    original = client.post("/predict", json=payload).json["prediction"][0]
    changed = copy.deepcopy(payload)
    changed["RM"]["0"] = 8.0
    other = client.post("/predict", json=changed).json["prediction"][0]
    assert original != pytest.approx(other)
    combined = {key: [payload[key]["0"], changed[key]["0"]] for key in FEATURES}
    together = client.post("/predict", json=combined)
    assert together.json["prediction"] == pytest.approx([original, other])


def test_column_order_does_not_change_prediction(client, payload):
    reversed_payload = dict(reversed(list(payload.items())))
    first = client.post("/predict", json=payload).json["prediction"]
    second = client.post("/predict", json=reversed_payload).json["prediction"]
    assert first == pytest.approx(second)


@pytest.mark.parametrize("bad_value", [None, "6.575", True, float("nan"),
                                        float("inf"), {}, [], 10 ** 400])
def test_rejects_invalid_feature_values(client, payload, bad_value):
    payload["RM"]["0"] = bad_value
    response = client.post("/predict", json=payload)
    assert response.status_code == 400
    assert "error" in response.json


@pytest.mark.parametrize("bad_payload", [None, [], {}, {"RM": {"0": 4}},
                                          {key: [] for key in FEATURES},
                                          {key: 1 for key in FEATURES}])
def test_rejects_invalid_schema(client, bad_payload):
    response = client.post("/predict", data=json.dumps(bad_payload),
                           content_type="application/json")
    assert response.status_code == 400


def test_rejects_extra_feature(client, payload):
    payload["unexpected"] = {"0": 1}
    assert client.post("/predict", json=payload).status_code == 400


def test_rejects_mismatched_row_identifiers(client, payload):
    payload["RM"] = {"1": 5.0}
    assert client.post("/predict", json=payload).status_code == 400


def test_rejects_mixed_column_containers(client, payload):
    payload["RM"] = [5.0]
    assert client.post("/predict", json=payload).status_code == 400


def test_rejects_unequal_arrays(client):
    payload = {key: [1.0] for key in FEATURES}
    payload["RM"].append(2.0)
    assert client.post("/predict", json=payload).status_code == 400


def test_rejects_oversized_request_and_too_many_rows(client):
    assert client.post("/predict", data="x" * 17000,
                       content_type="application/json").status_code == 413
    payload = {key: [1.0] * 101 for key in FEATURES}
    assert client.post("/predict", json=payload).status_code == 400


def test_content_type_and_malformed_json(client):
    assert client.post("/predict", data="{}").status_code == 415
    assert client.post("/predict", data="{bad", content_type="application/json").status_code == 400


def test_get_prediction_is_not_allowed(client):
    assert client.get("/predict").status_code == 405


def test_numerical_overflow_is_a_client_error(client, payload):
    payload["RM"]["0"] = 1e308
    assert client.post("/predict", json=payload).status_code == 400


def test_missing_model_is_unavailable(tmp_path, payload):
    service = create_app(tmp_path / "missing.joblib")
    service.config.update(TESTING=True)
    missing_client = service.test_client()
    assert missing_client.get("/health").status_code == 503
    assert missing_client.post("/predict", json=payload).status_code == 503


def test_prediction_is_logged_without_request_features(client, payload, caplog):
    with caplog.at_level("INFO"):
        response = client.post("/predict", json=payload)
    assert response.json["request_id"] in caplog.text
    assert "rows=1 values=" in caplog.text
    assert "396.9" not in caplog.text
