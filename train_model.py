from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

FEATURE_COLUMNS = [
    'transaction_amount',
    'transaction_time',
    'location_distance',
    'cardholder_age',
    'merchant_risk_score',
    'device_trust_score',
    'is_international',
]
TARGET_COLUMN = 'is_fraud'


def ensure_demo_dataset(dataset_path: str | Path, rows: int = 2500) -> None:
    dataset_path = Path(dataset_path)
    if dataset_path.exists():
        return

    rng = np.random.default_rng(42)
    amount = rng.uniform(5, 5000, rows)
    transaction_time = rng.uniform(0, 24, rows)
    location_distance = rng.uniform(0, 3000, rows)
    cardholder_age = rng.uniform(18, 75, rows)
    merchant_risk_score = rng.uniform(0, 100, rows)
    device_trust_score = rng.uniform(0, 100, rows)
    is_international = rng.integers(0, 2, rows)

    risk_signal = (
        (amount > 2500).astype(int)
        + (location_distance > 1200).astype(int)
        + (merchant_risk_score > 70).astype(int)
        + (device_trust_score < 30).astype(int)
        + is_international
        + ((transaction_time < 5) | (transaction_time > 23)).astype(int)
    )

    probability = np.clip(risk_signal / 6, 0, 1)
    is_fraud = (rng.random(rows) < probability * 0.75).astype(int)

    df = pd.DataFrame(
        {
            'transaction_amount': amount.round(2),
            'transaction_time': transaction_time.round(2),
            'location_distance': location_distance.round(2),
            'cardholder_age': cardholder_age.round(0),
            'merchant_risk_score': merchant_risk_score.round(2),
            'device_trust_score': device_trust_score.round(2),
            'is_international': is_international,
            'is_fraud': is_fraud,
        }
    )
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dataset_path, index=False)


def train_and_save_model(dataset_path: str | Path, model_path: str | Path, features_path: str | Path) -> None:
    dataset_path = Path(dataset_path)
    model_path = Path(model_path)
    features_path = Path(features_path)

    df = pd.read_csv(dataset_path)
    missing_cols = [col for col in FEATURE_COLUMNS + [TARGET_COLUMN] if col not in df.columns]
    if missing_cols:
        raise ValueError(f'Dataset is missing columns: {missing_cols}')

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=180,
        max_depth=10,
        class_weight='balanced',
        random_state=42,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    report = classification_report(y_test, preds)
    print(report)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    joblib.dump(FEATURE_COLUMNS, features_path)


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / 'data' / 'demo_creditcard_data.csv'
    ensure_demo_dataset(data_path)
    train_and_save_model(
        dataset_path=data_path,
        model_path=base_dir / 'model_artifacts' / 'fraud_model.joblib',
        features_path=base_dir / 'model_artifacts' / 'feature_columns.joblib',
    )
