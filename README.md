# Credit Card Fraud Detection - College Project Web App

A full-stack Flask project for a college submission.

## Features
- Professional landing page
- Manual fraud prediction form
- Batch CSV fraud checking
- SQLite database for prediction history
- ML model training script
- Easy deployment on Render, Railway, or PythonAnywhere
- Attractive UI using HTML, CSS, and JavaScript

## Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Flask
- Database: SQLite
- Machine Learning: Scikit-learn RandomForestClassifier

## Required Input Fields
Manual and CSV prediction use these columns:
- transaction_amount
- transaction_time
- location_distance
- cardholder_age
- merchant_risk_score
- device_trust_score
- is_international

## Local Run
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python train_model.py
python app.py
```

Open: http://127.0.0.1:5000

## Deployment
### Render / Railway
1. Upload project to GitHub
2. Create a new Web Service
3. Build command:
```bash
pip install -r requirements.txt && python train_model.py
```
4. Start command:
```bash
gunicorn app:app
```
5. Add environment variable:
- `SECRET_KEY=your_secret_key_here`

## Notes for Viva / Project Report
- The provided dataset is a synthetic demo dataset automatically generated for safe project use.
- For a real research-grade project, replace `data/demo_creditcard_data.csv` with a real fraud dataset using the same schema and retrain the model.
- You can discuss class imbalance, precision, recall, and fraud probability threshold in your project presentation.
