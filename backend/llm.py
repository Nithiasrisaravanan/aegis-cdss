import os
import requests
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

BOOKS = [
    "Harrison's Principles of Internal Medicine (21st Ed)",
    "Braunwald's Heart Disease (12th Ed)",
    "Davidson's Principles & Practice of Medicine (24th Ed)",
    "Robbins & Cotran Pathologic Basis of Disease (10th Ed)",
    "Gray's Anatomy (42nd Ed)"
]

def build_prompt(patient: dict, prediction: dict, shap: dict, articles: list) -> str:
    evidence = ""
    for a in articles[:5]:
        evidence += f"- {a['title']} [{a['journal']}, {a['year']}] PMID:{a['pmid']}\n"

    top_features = ", ".join(
        [f"{f['feature']}={f['input_value']} (SHAP:{f['value']})"
         for f in shap['features'][:5]]
    )

    books = "\n".join([f"- {b}" for b in BOOKS])

    return f"""You are a clinical decision support assistant. Based on the following 
data, generate a structured medical report. Only use the provided evidence.
Cite PMIDs inline as [PMID: xxxxx].

PATIENT DATA:
Age: {patient.get('age')}, Sex: {'Male' if patient.get('sex')==1 else 'Female'}
BP: {patient.get('trestbps')} mmHg, Cholesterol: {patient.get('chol')} mg/dL
Max HR: {patient.get('thalach')}, Chest Pain Type: {patient.get('cp')}
Fasting Blood Sugar >120: {patient.get('fbs')}, Exercise Angina: {patient.get('exang')}

ML PREDICTION:
Primary: {prediction['primary']['label']} ({prediction['primary']['probability']}%)
Baseline: {prediction['baseline']['label']} ({prediction['baseline']['probability']}%)

TOP SHAP FEATURES: {top_features}

THREE DIFFERENTIAL DIAGNOSES (ranked):
1. {prediction['differential'][0]['label']} - {prediction['differential'][0]['probability']}%
2. Consider: Stable Angina Pectoris
3. Consider: Hypertensive Heart Disease

RETRIEVED PUBMED EVIDENCE:
{evidence}

REFERENCE TEXTBOOKS:
{books}

Generate a report with these exact sections:
1. CLINICAL EXPLANATION
   - Profile: patient summary
   - Diagnostic: ML model findings
   - Pathophysiology: disease mechanism with [PMID: xxxxx] citations
   - Comorbidities: related conditions to monitor

2. EVIDENCE-BASED TREATMENT OPTIONS
   - List 3-4 treatments with citations

3. EXTRACTED SUPPORT ACTIONS
   - Symptomatic Management
   - Monitoring & Follow-up
   - Lifestyle Modifications
   - Referral Recommendations

Keep it clinical, concise, and cite PMIDs inline. Reference textbooks where appropriate.
End with: "Decision support only — clinician makes final diagnosis."
"""

def generate_gemini(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini failed: {e}")
        return None

def generate_ollama(prompt: str) -> str:
    try:
        r = requests.post("http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": prompt, "stream": False},
            timeout=60)
        return r.json().get("response", "")
    except Exception as e:
        print(f"Ollama failed: {e}")
        return None

def generate_template(patient: dict, prediction: dict) -> str:
    label = prediction['primary']['label']
    prob  = prediction['primary']['probability']
    return f"""
1. CLINICAL EXPLANATION
   - Profile: Patient Age {patient.get('age')}, presenting for cardiac assessment.
   - Diagnostic: ML model predicts {label} with {prob}% confidence.
   - Pathophysiology: Based on clinical features including chest pain type,
     ST depression, and vessel count, cardiac risk is evaluated.
   - Comorbidities: Monitor for hypertension, diabetes, and dyslipidemia.

2. EVIDENCE-BASED TREATMENT OPTIONS
   - Lifestyle modification: diet, exercise, smoking cessation.
   - Pharmacotherapy: statins, beta-blockers, ACE inhibitors as indicated.
   - Further workup: stress test, echocardiogram, coronary angiography.

3. EXTRACTED SUPPORT ACTIONS
   - Symptomatic Management: Monitor BP and HR regularly.
   - Monitoring: Regular ECG and lipid panel follow-up.
   - Lifestyle: Mediterranean diet and 150 min/week aerobic exercise.
   - Referral: Cardiology consultation recommended.

Decision support only — clinician makes final diagnosis.
"""

def generate_report(patient: dict, prediction: dict, shap: dict, articles: list) -> str:
    prompt = build_prompt(patient, prediction, shap, articles)

    # Tier 1: Gemini
    result = generate_gemini(prompt)
    if result:
        print("Used: Gemini")
        return result

    # Tier 2: Ollama
    result = generate_ollama(prompt)
    if result:
        print("Used: Ollama")
        return result

    # Tier 3: Template
    print("Used: Template fallback")
    return generate_template(patient, prediction)

if __name__ == '__main__':
    from model import predict
    from explain import explain
    from rag import retrieve_evidence

    patient = {
        'age': 63, 'sex': 1, 'cp': 1, 'trestbps': 145,
        'chol': 233, 'fbs': 1, 'restecg': 2, 'thalach': 150,
        'exang': 0, 'oldpeak': 2.3, 'slope': 3, 'ca': 0, 'thal': 6
    }

    print("Running prediction...")
    prediction = predict(patient)
    print("Running SHAP...")
    shap = explain(patient)
    print("Fetching evidence...")
    articles = retrieve_evidence("heart disease", ["chest pain", "cholesterol"])
    print("Generating report...")
    report = generate_report(patient, prediction, shap, articles)
    print("\n" + "="*60)
    print(report[:1500])