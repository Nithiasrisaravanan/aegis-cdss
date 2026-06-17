import numpy as np
from sentence_transformers import SentenceTransformer
from nih_api import search_pubmed, fetch_summaries, fetch_abstract

model = SentenceTransformer('all-MiniLM-L6-v2')

FEATURE_LABELS = {
    'age': 'age risk factor',
    'sex': 'sex gender risk factor',
    'cp': 'chest pain type',
    'trestbps': 'resting blood pressure',
    'chol': 'serum cholesterol',
    'fbs': 'fasting blood sugar diabetes',
    'restecg': 'resting electrocardiogram ECG',
    'thalach': 'maximum heart rate exercise',
    'exang': 'exercise induced angina',
    'oldpeak': 'ST depression exercise',
    'slope': 'slope ST segment',
    'ca': 'number vessels fluoroscopy',
    'thal': 'thalassemia defect'
}

def compute_credibility(feature: str, disease: str, shap_value: float) -> dict:
    feature_label = FEATURE_LABELS.get(feature, feature)
    query = f"{feature_label} {disease} diagnosis prognosis"

    # Search PubMed for this feature + disease
    pmids = search_pubmed(query, max_results=3)
    if not pmids:
        return {
            "feature": feature,
            "shap_value": round(shap_value, 4),
            "credibility_pct": 0.0,
            "citation_label": "No evidence found",
            "citation_url": "",
            "flagged": abs(shap_value) > 0.05
        }

    articles = fetch_summaries(pmids)
    if not articles:
        return {
            "feature": feature,
            "shap_value": round(shap_value, 4),
            "credibility_pct": 0.0,
            "citation_label": "No evidence found",
            "citation_url": "",
            "flagged": abs(shap_value) > 0.05
        }

    # Get abstract for top article
    top = articles[0]
    abstract = fetch_abstract(top["pmid"])
    passage = f"{top['title']}. {abstract[:300]}"

    # Cosine similarity between query and passage
    q_emb = model.encode([query], convert_to_numpy=True)
    p_emb = model.encode([passage], convert_to_numpy=True)
    q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)
    p_emb = p_emb / np.linalg.norm(p_emb, axis=1, keepdims=True)
    similarity = float(np.dot(q_emb, p_emb.T)[0][0])
    credibility_pct = round(min(similarity * 150, 100.0), 1)

    # Flag if high SHAP but low credibility
    flagged = abs(shap_value) > 0.05 and credibility_pct < 40.0

    return {
        "feature": feature,
        "shap_value": round(shap_value, 4),
        "credibility_pct": credibility_pct,
        "citation_label": f"{top['title'][:60]}... | PMID:{top['pmid']}",
        "citation_url": top["url"],
        "flagged": flagged
    }

def score_all_features(shap_features: list, disease: str) -> list:
    results = []
    for f in shap_features[:6]:  # top 6 features
        print(f"  Scoring: {f['feature']}...")
        result = compute_credibility(f['feature'], disease, f['value'])
        results.append(result)
    return results

if __name__ == '__main__':
    test_features = [
        {"feature": "cp", "value": -0.1333},
        {"feature": "ca", "value": -0.1148},
        {"feature": "oldpeak", "value": 0.035},
    ]
    print("Computing credibility scores...")
    results = score_all_features(test_features, "heart disease")
    print("\nCredibility Results:")
    for r in results:
        flag = "⚠️" if r["flagged"] else "✅"
        print(f"  {flag} {r['feature']}: SHAP={r['shap_value']} | Credibility={r['credibility_pct']}%")
        print(f"     Citation: {r['citation_label']}")