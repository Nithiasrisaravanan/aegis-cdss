from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

from model import predict
from explain import explain
from rag import retrieve_evidence
from llm import generate_report
from credibility import score_all_features
from myhealthbox_api import get_medicines, get_stockist_coords
from prescriptions import publish_prescription, get_all_prescriptions
app = FastAPI(title="Aegis CDSS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class PatientInput(BaseModel):
    age: float
    sex: float
    cp: float
    trestbps: float
    chol: float
    fbs: float
    restecg: float
    thalach: float
    exang: float
    oldpeak: float
    slope: float
    ca: float
    thal: float

class PrescriptionInput(BaseModel):
    patient_name: str
    age: int
    gender: str
    diagnosis: str
    report: str
    medicines: list

@app.get("/")
def root():
    return {"status": "Aegis CDSS API running"}

@app.post("/predict")
def predict_endpoint(patient: PatientInput):
    try:
        data = patient.dict()
        result = predict(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain")
def explain_endpoint(patient: PatientInput):
    try:
        data = patient.dict()
        result = explain(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
def analyze_endpoint(patient: PatientInput):
    try:
        data = patient.dict()

        # Step 1: Predict
        prediction = predict(data)
        disease = prediction["primary"]["label"]

        # Step 2: SHAP
        shap = explain(data)

        # Step 3: Evidence
        features = [f["feature"] for f in shap["features"][:3]]
        articles = retrieve_evidence(disease, features)

        # Step 4: Credibility
        credibility = score_all_features(shap["features"], disease)

        # Step 5: LLM Report
        report = generate_report(data, prediction, shap, articles)

        # Step 6: Medicines
        medicines = get_medicines(disease)
        for m in medicines:
            m["coords"] = get_stockist_coords(m["stockists"])

        return {
            "prediction": prediction,
            "shap": shap,
            "credibility": credibility,
            "articles": articles,
            "report": report,
            "medicines": medicines
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def metrics_endpoint():
    try:
        with open("models/metrics.json") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/prescriptions")
def save_prescription(data: PrescriptionInput):
    try:
        record = publish_prescription(
            patient_name=data.patient_name,
            age=data.age,
            gender=data.gender,
            diagnosis=data.diagnosis,
            report=data.report,
            medicines=data.medicines
        )
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prescriptions")
def list_prescriptions():
    try:
        return get_all_prescriptions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))