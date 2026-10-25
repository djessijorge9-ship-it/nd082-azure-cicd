"""Validated prediction service for the Udacity CI/CD starter model.

The supplied LinearRegression model was trained on six unscaled columns. Never
fit a scaler to inference batches: doing that makes one-row predictions constant.
"""

import logging
import math
from numbers import Real
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request
import joblib
import pandas as pd
import numpy as np
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

FEATURES = ("CHAS", "RM", "TAX", "PTRATIO", "B", "LSTAT")
DEFAULT_MODEL = Path(__file__).parent / "Housing_price_model" / "LinearRegression.joblib"
MAX_ROWS = 100


def finite_number(value):
    """Reject booleans, non-numbers and integers outside floating point range."""
    if isinstance(value, bool) or not isinstance(value, Real):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def validate_payload(payload):
    """Return finite, ordered numeric rows from the starter's column JSON format."""
    if not isinstance(payload, dict) or set(payload) != set(FEATURES):
        raise ValueError("JSON must contain exactly these columns: " + ", ".join(FEATURES))
    if not all(isinstance(payload[key], (dict, list)) for key in FEATURES):
        raise ValueError("Each column must be an object or array containing numeric rows")
    first = payload[FEATURES[0]]
    if not first or len(first) > MAX_ROWS:
        raise ValueError(f"Provide between 1 and {MAX_ROWS} rows")
    if isinstance(first, dict):
        if not all(isinstance(payload[key], dict) and set(payload[key]) == set(first)
                   for key in FEATURES):
            raise ValueError("Column row identifiers must match")
        values = [[payload[column][row] for column in FEATURES] for row in first]
    else:
        if not all(isinstance(payload[key], list) and len(payload[key]) == len(first)
                   for key in FEATURES):
            raise ValueError("Columns must contain matching arrays")
        values = [[payload[column][row] for column in FEATURES] for row in range(len(first))]
    if any(not finite_number(value) for row in values for value in row):
        raise ValueError("Every feature must be a finite number; strings and booleans are invalid")
    return pd.DataFrame(values, columns=FEATURES, dtype=float)


def create_app(model_path=DEFAULT_MODEL):
    """Create a service; model availability is exposed by the readiness endpoint."""
    service = Flask(__name__)
    service.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    service.logger.setLevel(logging.INFO)
    try:
        model = joblib.load(model_path)
        if getattr(model, "n_features_in_", None) != len(FEATURES):
            raise ValueError("The model feature count does not match the API contract")
    except (OSError, ValueError, TypeError) as error:
        service.logger.error("Model unavailable: %s", error)
        model = None

    @service.get("/")
    def home():
        return "<h3>Sklearn Prediction Home</h3><p>Educational housing model: POST /predict</p>"

    @service.get("/health")
    def health():
        code = 200 if model is not None else 503
        return jsonify(status="ready" if model is not None else "unavailable",
                       model="Udacity LinearRegression", features=list(FEATURES)), code

    @service.errorhandler(RequestEntityTooLarge)
    def oversized(_error):
        return jsonify(error="JSON request body exceeds the 16 KiB limit"), 413

    @service.post("/predict")
    def predict():
        if model is None:
            return jsonify(error="Prediction model is unavailable"), 503
        if not request.is_json:
            return jsonify(error="Content-Type must be application/json"), 415
        try:
            frame = validate_payload(request.get_json())
        except (BadRequest, ValueError) as error:
            message = "Malformed JSON" if isinstance(error, BadRequest) else str(error)
            return jsonify(error=message), 400
        # The original LinearRegression was trained with an unnamed numeric array.
        try:
            with np.errstate(over="raise", invalid="raise"):
                predictions = model.predict(frame.to_numpy()).tolist()
        except (FloatingPointError, ValueError):
            return jsonify(error="Features exceed the model's supported numerical range"), 400
        if not all(math.isfinite(value) for value in predictions):
            service.logger.error("Prediction produced a non-finite value")
            return jsonify(error="Prediction failed"), 500
        request_id = uuid4().hex
        service.logger.info("prediction request_id=%s rows=%d values=%s",
                            request_id, len(predictions), predictions)
        return jsonify(prediction=predictions, request_id=request_id)

    return service


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
