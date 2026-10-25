"""Reproduce the starter notebook's six-feature regression with installed sklearn.

This historical dataset is retained solely for the course deployment exercise.
It contains a racially constructed feature and is unsuitable for housing decisions.
"""
import hashlib
import json
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("CRIM", "ZN", "INDUS", "CHAS", "NOX", "RM", "AGE", "DIS", "RAD", "TAX",
         "PTRATIO", "B", "LSTAT", "MEDV")
FEATURES = ("CHAS", "RM", "TAX", "PTRATIO", "B", "LSTAT")


def main():
    data_path = ROOT / "housing.csv"
    frame = pd.read_csv(data_path, sep=r"\s+", names=NAMES)
    features = frame.loc[:, FEATURES].to_numpy()
    target = frame["MEDV"].to_numpy()
    train_x, test_x, train_y, test_y = train_test_split(
        features, target, test_size=0.20, random_state=7)
    model = LinearRegression().fit(train_x, train_y)
    model_path = ROOT / "Housing_price_model" / "LinearRegression.joblib"
    joblib.dump(model, model_path)
    metadata = {
        "source": "Udacity official starter Boston_housing_predict.ipynb and housing.csv",
        "dataset_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
        "features": FEATURES,
        "preprocessing": "No scaling: raw six numeric features, matching notebook LinearRegression",
        "sklearn_version": sklearn.__version__,
        "random_state": 7,
        "train_rows": len(train_x),
        "test_rows": len(test_x),
        "test_mse": float(mean_squared_error(test_y, model.predict(test_x))),
        "coefficient": model.coef_.tolist(),
        "intercept": float(model.intercept_),
        "scope": "Educational legacy deployment sample; not for real housing decisions"
    }
    (model_path.parent / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
