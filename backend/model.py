import joblib
import numpy as np
import pandas as pd
import os
from diagnosis_mapper import map_to_specific_diagnosis
from ecg_model import predict_ecg, fuse_predictions

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rf_model = joblib.load(os.path.join(BASE_DIR, 'models', 'tabpfn_model.pkl'))
dt_model = joblib.load(os.path.join(BASE_DIR, 'models', 'decision_tree_model.pkl'))

FEATURES = ['age','sex','cp','trestbps','chol','fbs',
            'restecg','thalach','exang','oldpeak','slope','ca','thal']

LABELS = {0: 'No Heart Disease', 1: 'Heart Disease Present'}

def prepare_input(patient: dict) -> pd.DataFrame:
    row = {f: patient.get(f, 0) for f in FEATURES}
    return pd.DataFrame([row])

def predict(patient: dict) -> dict:
    X = prepare_input(patient)

    # Primary model (Random Forest)
    rf_proba = rf_model.predict_proba(X)[0]
    rf_class = int(np.argmax(rf_proba))
    rf_confidence = float(rf_proba[rf_class])

    # Baseline model (Decision Tree)
    dt_proba = dt_model.predict_proba(X)[0]
    dt_class = int(np.argmax(dt_proba))

    # Specific diagnosis mapping
    specific_diagnosis = map_to_specific_diagnosis(patient, rf_class, rf_confidence)

    # Differential diagnosis
    no_disease_prob = round(float(rf_proba[0]) * 100, 1)
    disease_prob = round(float(rf_proba[1]) * 100, 1)

    if rf_class == 1:
        differential = [
            {"label": specific_diagnosis["label"], "probability": disease_prob},
            {"label": "Stable Angina Pectoris (alternate consideration)", "probability": round(disease_prob * 0.6, 1)},
            {"label": "No Cardiac Abnormality", "probability": no_disease_prob},
        ]
    else:
        differential = [
            {"label": specific_diagnosis["label"], "probability": no_disease_prob},
            {"label": "Hypertensive Heart Disease (if risk factors persist)", "probability": disease_prob},
        ]

    # ECG Fusion (optional)
    ecg_signal = patient.get('ecg_signal', None)
    if ecg_signal and len(ecg_signal) > 0:
        ecg_result = predict_ecg(ecg_signal)
        fusion = fuse_predictions(
            tabular_prob=rf_confidence,
            ecg_risk_score=ecg_result['ecg_risk_score'],
            ecg_available=ecg_result['ecg_available']
        )
    else:
        ecg_result = {
            "ecg_available": False,
            "ecg_class": "Not provided",
            "ecg_risk_score": 0.0,
            "ecg_probabilities": {}
        }
        fusion = fuse_predictions(rf_confidence, 0.0, False)

    return {
        "primary": {
            "class": rf_class,
            "label": specific_diagnosis["label"],
            "description": specific_diagnosis["description"],
            "probability": round(rf_confidence * 100, 1),
            "fused_probability": fusion["fused_probability"],
            "model": "Random Forest"
        },
        "baseline": {
            "class": dt_class,
            "label": LABELS[dt_class],
            "probability": round(float(dt_proba[dt_class]) * 100, 1),
            "model": "Decision Tree"
        },
        "differential": differential,
        "confidence": {
            "score": round(rf_confidence * 100, 1),
            "reliable": rf_confidence >= 0.60,
            "models_agree": rf_class == dt_class
        },
        "ecg": ecg_result,
        "fusion": fusion,
        "input_features": patient
    }

if __name__ == '__main__':
    test_patient = {
        'age': 63, 'sex': 1, 'cp': 1, 'trestbps': 145,
        'chol': 233, 'fbs': 1, 'restecg': 2, 'thalach': 150,
        'exang': 0, 'oldpeak': 2.3, 'slope': 3, 'ca': 0, 'thal': 6
    }
    result = predict(test_patient)
    print("\nTest Patient Prediction:")
    print(f"  Primary: {result['primary']['label']} ({result['primary']['probability']}%)")
    print(f"  Fused Probability: {result['primary']['fused_probability']}%")
    print(f"  ECG: {result['ecg']['ecg_class']}")
    print(f"  Fusion Used: {result['fusion']['fusion_used']}")
    print(f"  Differential: {result['differential']}")