import json
import os
from datetime import datetime

PRESCRIPTIONS_FILE = "models/prescriptions.json"

def _load() -> list:
    if not os.path.exists(PRESCRIPTIONS_FILE):
        return []
    with open(PRESCRIPTIONS_FILE, "r") as f:
        return json.load(f)

def _save(data: list):
    with open(PRESCRIPTIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def publish_prescription(
    patient_name: str,
    age: int,
    gender: str,
    diagnosis: str,
    report: str,
    medicines: list
) -> dict:
    prescriptions = _load()
    record = {
        "id": len(prescriptions) + 1,
        "patient_name": patient_name,
        "age": age,
        "gender": gender,
        "diagnosis": diagnosis,
        "report": report,
        "medicines": medicines,
        "issued_on": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": "Active"
    }
    prescriptions.append(record)
    _save(prescriptions)
    return record

def get_all_prescriptions() -> list:
    return _load()

def get_prescription(patient_name: str) -> dict:
    prescriptions = _load()
    for p in reversed(prescriptions):
        if p["patient_name"].lower() == patient_name.lower():
            return p
    return None

if __name__ == '__main__':
    rec = publish_prescription(
        patient_name="Surendhar",
        age=63,
        gender="Male",
        diagnosis="No Heart Disease",
        report="Patient shows no significant cardiac abnormality...",
        medicines=["Amlodipine", "Aspirin"]
    )
    print(f"Published: {rec['patient_name']} | {rec['diagnosis']} | {rec['issued_on']}")

    all_p = get_all_prescriptions()
    print(f"Total prescriptions: {len(all_p)}")