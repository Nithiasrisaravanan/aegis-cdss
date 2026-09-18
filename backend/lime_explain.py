import numpy as np
import pandas as pd
import joblib
import os
from lime.lime_tabular import LimeTabularExplainer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rf_model = joblib.load(os.path.join(BASE_DIR, 'models', 'tabpfn_model.pkl'))

FEATURES = ['age','sex','cp','trestbps','chol','fbs',
            'restecg','thalach','exang','oldpeak','slope','ca','thal']

df = pd.read_csv(os.path.join(BASE_DIR, 'data', 'dataset.csv'))
X_train = df.drop('target', axis=1).values

explainer = LimeTabularExplainer(
    training_data=X_train,
    feature_names=FEATURES,
    class_names=['No Disease', 'Heart Disease'],
    mode='classification',
    random_state=42
)

def explain_lime(patient: dict, num_features: int = 13) -> dict:
    row = np.array([patient.get(f, 0) for f in FEATURES], dtype=float)
    explanation = explainer.explain_instance(
        data_row=row,
        predict_fn=rf_model.predict_proba,
        num_features=num_features,
        num_samples=1000
    )
    lime_weights = explanation.as_list(label=1)
    features = []
    for feature_desc, weight in lime_weights:
        feature_name = None
        for f in FEATURES:
            if f in feature_desc:
                feature_name = f
                break
        if not feature_name:
            feature_name = feature_desc
        features.append({
            "feature": feature_name,
            "feature_desc": feature_desc,
            "value": round(float(weight), 4),
            "direction": "up" if weight > 0 else "down"
        })
    features.sort(key=lambda x: abs(x["value"]), reverse=True)
    return {
        "features": features,
        "method": "LIME",
        "num_samples": 1000
    }

if __name__ == '__main__':
    test_patient = {
        'age': 63, 'sex': 1, 'cp': 1, 'trestbps': 145,
        'chol': 233, 'fbs': 1, 'restecg': 2, 'thalach': 150,
        'exang': 0, 'oldpeak': 2.3, 'slope': 3, 'ca': 0, 'thal': 6
    }
    result = explain_lime(test_patient)
    print("\nLIME Feature Explanations:")
    for f in result['features'][:5]:
        arrow = "up" if f['direction'] == 'up' else "down"
        print(f"  {arrow} {f['feature']}: {f['value']}")