import joblib
import numpy as np
import pandas as pd
import os
from diagnosis_mapper import map_to_specific_diagnosis

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

    rf_proba = rf_model.predict_proba(X)[0]
    rf_class = int(np.argmax(rf_proba))
    rf_confidence = float(rf_proba[rf_class])

    dt_proba = dt_model.predict_proba(X)[0]
    dt_class = int(np.argmax(dt_proba))

    specific_diagnosis = map_to_specific_diagnosis(patient, rf_class, rf_confidence)

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
       
    return {
        "primary": {
            "class": rf_class,
            "label": specific_diagnosis["label"],
            "description": specific_diagnosis["description"],
            "probability": round(rf_confidence * 100, 1),
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
    print(f"  Description: {result['primary']['description']}")
    print(f"  Baseline: {result['baseline']['label']} ({result['baseline']['probability']}%)")
    print(f"  Confidence: {result['confidence']['score']}%")
    print(f"  Differential: {result['differential']}")