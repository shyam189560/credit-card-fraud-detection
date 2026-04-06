from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import joblib
import pandas as pd
from flask import Flask, flash, redirect, render_template, request, url_for

from train_model import ensure_demo_dataset, train_and_save_model

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'fraud_app.db'
MODEL_PATH = BASE_DIR / 'model_artifacts' / 'fraud_model.joblib'
FEATURES_PATH = BASE_DIR / 'model_artifacts' / 'feature_columns.joblib'
UPLOAD_DIR = BASE_DIR / 'data' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'college-project-demo-secret')


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db_connection()
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_amount REAL,
            transaction_time REAL,
            location_distance REAL,
            cardholder_age REAL,
            merchant_risk_score REAL,
            device_trust_score REAL,
            is_international INTEGER,
            fraud_probability REAL,
            prediction_label TEXT,
            created_at TEXT
        )
        '''
    )
    conn.commit()
    conn.close()


def ensure_model() -> None:
    if not MODEL_PATH.exists() or not FEATURES_PATH.exists():
        ensure_demo_dataset(BASE_DIR / 'data' / 'demo_creditcard_data.csv')
        train_and_save_model(
            dataset_path=BASE_DIR / 'data' / 'demo_creditcard_data.csv',
            model_path=MODEL_PATH,
            features_path=FEATURES_PATH,
        )


def load_model_and_features():
    model = joblib.load(MODEL_PATH)
    feature_columns: List[str] = joblib.load(FEATURES_PATH)
    return model, feature_columns


def bool_from_form(value: str | None) -> int:
    return 1 if value in {'1', 'true', 'on', 'yes'} else 0


def build_feature_row(form_data: Dict[str, str]) -> Dict[str, float]:
    return {
        'transaction_amount': float(form_data['transaction_amount']),
        'transaction_time': float(form_data['transaction_time']),
        'location_distance': float(form_data['location_distance']),
        'cardholder_age': float(form_data['cardholder_age']),
        'merchant_risk_score': float(form_data['merchant_risk_score']),
        'device_trust_score': float(form_data['device_trust_score']),
        'is_international': bool_from_form(form_data.get('is_international')),
    }


def save_prediction(row: Dict[str, float], probability: float, label: str) -> None:
    conn = get_db_connection()
    conn.execute(
        '''
        INSERT INTO predictions (
            transaction_amount, transaction_time, location_distance, cardholder_age,
            merchant_risk_score, device_trust_score, is_international,
            fraud_probability, prediction_label, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            row['transaction_amount'],
            row['transaction_time'],
            row['location_distance'],
            row['cardholder_age'],
            row['merchant_risk_score'],
            row['device_trust_score'],
            row['is_international'],
            probability,
            label,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        ),
    )
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            model, feature_columns = load_model_and_features()
            feature_row = build_feature_row(request.form)
            df = pd.DataFrame([feature_row])
            df = df[feature_columns]
            probability = float(model.predict_proba(df)[0][1])
            label = 'Fraud Detected' if probability >= 0.50 else 'Legitimate Transaction'
            save_prediction(feature_row, probability, label)
            return render_template(
                'result.html',
                probability=round(probability * 100, 2),
                label=label,
                form_data=feature_row,
            )
        except Exception as exc:
            flash(f'Prediction failed: {exc}', 'danger')
            return redirect(url_for('predict'))

    return render_template('predict.html')


@app.route('/batch', methods=['GET', 'POST'])
def batch_predict():
    batch_results = None
    if request.method == 'POST':
        file = request.files.get('csv_file')
        if not file or not file.filename.lower().endswith('.csv'):
            flash('Please upload a valid CSV file.', 'danger')
            return redirect(url_for('batch_predict'))

        upload_path = UPLOAD_DIR / file.filename
        file.save(upload_path)

        try:
            model, feature_columns = load_model_and_features()
            df = pd.read_csv(upload_path)
            missing = [col for col in feature_columns if col not in df.columns]
            if missing:
                flash(f'Missing required columns: {", ".join(missing)}', 'danger')
                return redirect(url_for('batch_predict'))

            scored = df.copy()
            scored = scored[feature_columns]
            probs = model.predict_proba(scored)[:, 1]
            labels = ['Fraud Detected' if p >= 0.50 else 'Legitimate Transaction' for p in probs]

            preview = df.copy()
            preview['fraud_probability'] = (probs * 100).round(2)
            preview['prediction_label'] = labels
            batch_results = preview.head(15).to_dict(orient='records')
        except Exception as exc:
            flash(f'Batch prediction failed: {exc}', 'danger')
            return redirect(url_for('batch_predict'))

    return render_template('batch.html', batch_results=batch_results)


@app.route('/history')
def history():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM predictions ORDER BY id DESC LIMIT 50').fetchall()
    conn.close()
    return render_template('history.html', rows=rows)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/train-demo-model')
def train_demo_model():
    try:
        ensure_demo_dataset(BASE_DIR / 'data' / 'demo_creditcard_data.csv')
        train_and_save_model(
            dataset_path=BASE_DIR / 'data' / 'demo_creditcard_data.csv',
            model_path=MODEL_PATH,
            features_path=FEATURES_PATH,
        )
        flash('Demo fraud detection model retrained successfully.', 'success')
    except Exception as exc:
        flash(f'Model training failed: {exc}', 'danger')
    return redirect(url_for('about'))


if __name__ == '__main__':
    init_db()
    ensure_model()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
else:
    init_db()
    ensure_model()
