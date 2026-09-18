import numpy as np
from explain import explain
from lime_explain import explain_lime
from credibility import compute_credibility

def compare_shap_lime(patient: dict, disease: str = "heart disease") -> dict:
    """
    Compare SHAP and LIME explanations and credibility scores.
    Returns a side-by-side comparison table.
    """
    print("Running SHAP...")
    shap_result = explain(patient)
    
    print("Running LIME...")
    lime_result = explain_lime(patient)

    # Get top 6 features from each
    shap_features = {f["feature"]: f for f in shap_result["features"][:6]}
    lime_features = {f["feature"]: f for f in lime_result["features"][:6]}

    # Get union of all features
    all_features = list(set(list(shap_features.keys()) + list(lime_features.keys())))

    comparison = []
    for feature in all_features:
        shap_val = shap_features.get(feature, {}).get("value", 0.0)
        lime_val = lime_features.get(feature, {}).get("value", 0.0)

        # Agreement: both same direction
        shap_dir = "up" if shap_val > 0 else "down"
        lime_dir = "up" if lime_val > 0 else "down"
        agree = shap_dir == lime_dir

        # Credibility for this feature
        print(f"  Credibility scoring: {feature}...")
        cred = compute_credibility(feature, disease, shap_val)

        comparison.append({
            "feature": feature,
            "shap_value": round(shap_val, 4),
            "lime_value": round(lime_val, 4),
            "shap_direction": shap_dir,
            "lime_direction": lime_dir,
            "agreement": agree,
            "credibility_pct": cred["credibility_pct"],
            "citation_label": cred["citation_label"],
            "citation_url": cred["citation_url"],
            "flagged": cred["flagged"]
        })

    # Sort by average absolute importance
    comparison.sort(
        key=lambda x: (abs(x["shap_value"]) + abs(x["lime_value"])) / 2,
        reverse=True
    )

    # Summary stats
    total = len(comparison)
    agreed = sum(1 for c in comparison if c["agreement"])
    disagreed = total - agreed

    return {
        "comparison": comparison,
        "summary": {
            "total_features": total,
            "agreed": agreed,
            "disagreed": disagreed,
            "agreement_rate": round(agreed / total * 100, 1) if total > 0 else 0
        },
        "shap_base_value": shap_result["base_value"]
    }

if __name__ == '__main__':
    test_patient = {
        'age': 63, 'sex': 1, 'cp': 1, 'trestbps': 145,
        'chol': 233, 'fbs': 1, 'restecg': 2, 'thalach': 150,
        'exang': 0, 'oldpeak': 2.3, 'slope': 3, 'ca': 0, 'thal': 6
    }
    print("Running SHAP vs LIME comparison...")
    result = compare_shap_lime(test_patient)
    print(f"\nAgreement Rate: {result['summary']['agreement_rate']}%")
    print(f"Agreed: {result['summary']['agreed']} | Disagreed: {result['summary']['disagreed']}")
    print("\nComparison Table:")
    print(f"{'Feature':<12} {'SHAP':>8} {'LIME':>8} {'Agree':>6} {'Credibility':>12}")
    print("-" * 55)
    for c in result['comparison']:
        agree_str = "✅" if c['agreement'] else "❌"
        flag_str = "⚠" if c['flagged'] else ""
        print(f"{c['feature']:<12} {c['shap_value']:>8} {c['lime_value']:>8} {agree_str:>6} {c['credibility_pct']:>10}% {flag_str}")