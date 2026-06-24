def map_to_specific_diagnosis(patient: dict, primary_class: int, probability: float) -> dict:
    """
    Maps binary ML prediction + clinical features into a specific
    heart-related diagnosis using established clinical heuristics.
    """
    cp = patient.get('cp', 0)
    exang = patient.get('exang', 0)
    oldpeak = patient.get('oldpeak', 0)
    slope = patient.get('slope', 0)
    ca = patient.get('ca', 0)
    thal = patient.get('thal', 2)
    trestbps = patient.get('trestbps', 120)
    restecg = patient.get('restecg', 0)
    chol = patient.get('chol', 200)

    if primary_class == 0:
        # No disease detected, but check for borderline risk
        if trestbps > 140 or chol > 240:
            return {
                "label": "Subclinical Cardiovascular Risk",
                "description": "No structural heart disease detected, but elevated BP/cholesterol indicate early risk requiring monitoring."
            }
        return {
            "label": "No Cardiac Abnormality Detected",
            "description": "Clinical and ML indicators show no significant evidence of heart disease."
        }

    # Disease present — narrow down specific type
    if ca >= 2 and thal == 3:
        return {
            "label": "Coronary Artery Disease (Multi-vessel)",
            "description": "Multiple blocked vessels (fluoroscopy) with reversible perfusion defect strongly indicate multi-vessel CAD."
        }

    if exang == 1 and oldpeak > 2.0 and slope == 0:
        return {
            "label": "Unstable Angina",
            "description": "Exercise-induced angina with significant ST depression suggests unstable/high-risk angina."
        }

    if cp == 0 and exang == 1:
        return {
            "label": "Stable Angina Pectoris",
            "description": "Typical angina pattern with exercise-induced symptoms consistent with stable angina."
        }

    if trestbps > 140 and restecg in [1, 2]:
        return {
            "label": "Hypertensive Heart Disease",
            "description": "Elevated blood pressure with ECG abnormalities (LV hypertrophy/ST-T changes) suggests hypertensive heart disease."
        }

    if restecg == 1:
        return {
            "label": "Cardiac Arrhythmia (ECG Abnormality)",
            "description": "ST-T wave abnormality on resting ECG suggests possible arrhythmic or ischemic changes."
        }

    if ca >= 1:
        return {
            "label": "Coronary Artery Disease",
            "description": "Narrowed coronary vessels detected via fluoroscopy indicate coronary artery disease."
        }

    return {
        "label": "Ischemic Heart Disease",
        "description": "Overall clinical and ML pattern is consistent with ischemic heart disease; further cardiac workup recommended."
    }


if __name__ == '__main__':
    test_patient = {
        'age': 63, 'sex': 1, 'cp': 1, 'trestbps': 145,
        'chol': 233, 'fbs': 1, 'restecg': 2, 'thalach': 150,
        'exang': 0, 'oldpeak': 2.3, 'slope': 3, 'ca': 0, 'thal': 6
    }
    result = map_to_specific_diagnosis(test_patient, 1, 0.85)
    print(result)