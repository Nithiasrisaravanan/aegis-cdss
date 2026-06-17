import shap
import numpy as np
import pandas as pd
from model import rf_model, dt_model, prepare_input, FEATURES

def explain(patient: dict, model_type: str = "primary") -> dict:
    X = prepare_input(patient)
    model = rf_model if model_type == "primary" else dt_model

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Handle both 2D and 3D shap output formats
    if isinstance(shap_values, list):
        values = shap_values[1][0]
        base_value = float(explainer.expected_value[1])
    else:
        if shap_values.ndim == 3:
            values = shap_values[0, :, 1]
            base_value = float(explainer.expected_value[1])
        else:
            values = shap_values[0]
            base_value = float(explainer.expected_value)

    features = []
    for i, f in enumerate(FEATURES):
        val = float(values[i])
        features.append({
            "feature": f,
            "value": round(val, 4),
            "input_value": float(X[f].iloc[0]),
            "direction": "up" if val > 0 else "down"
        })

    features.sort(key=lambda x: abs(x["value"]), reverse=True)

    return {
        "base_value": round(base_value, 4),
        "features": features,
        "model": "Random Forest" if model_type == "primary" else "Decision Tree"
    }

if __name__ == '__main__':
    test_patient = {
        'age': 63, 'sex': 1, 'cp': 1, 'trestbps': 145,
        'chol': 233, 'fbs': 1, 'restecg': 2, 'thalach': 150,
        'exang': 0, 'oldpeak': 2.3, 'slope': 3, 'ca': 0, 'thal': 6
    }
    result = explain(test_patient)
    print(f"\nBase value: {result['base_value']}")
    print("\nTop SHAP features:")
    for f in result['features'][:5]:
        arrow = "↑" if f['direction'] == 'up' else "↓"
        print(f"  {arrow} {f['feature']}: {f['value']}")