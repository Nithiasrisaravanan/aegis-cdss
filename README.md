# ⚕ Aegis CDSS — AI-Enhanced Clinical Decision Support System

> **Decision support, not a diagnosis. The clinician makes the final call.**

Aegis CDSS is a full-stack, explainable AI-powered Clinical Decision Support System for heart disease prediction. It combines machine learning, SHAP explainability, live NIH PubMed evidence retrieval, and LLM-generated clinical reports into a single clinician-facing interface.

---

## 🌐 Live Demo

- **Frontend:** [https://aegis-cdss.vercel.app](https://aegis-cdss.vercel.app)
- **Backend (local):** [http://localhost:8000](http://localhost:8000)
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

> Note: The live frontend requires the backend running locally. See setup instructions below.

---

## ✨ Features

- 🧠 **ML Prediction** — Random Forest (86.7% accuracy, 93.75% ROC-AUC) + Decision Tree baseline
- 🔍 **SHAP Explainability** — Signed per-feature contribution scores with visual bar chart
- 📊 **Evidence-Validated Credibility Scoring** — Cross-validates SHAP features against live PubMed literature (novel contribution)
- 📚 **NIH PubMed RAG** — Live retrieval + FAISS semantic ranking of biomedical abstracts
- 🤖 **LLM Clinical Reports** — Gemini → Ollama → Template fallback, all claims cited to real PMIDs
- 💊 **Medicine Recommendations** — Indian pharmacy stockists + alternative brand names
- 👨‍⚕️ **Patient Portal** — Read-only prescription view for published reports
- 🏥 **Differential Diagnosis** — Specific named cardiac conditions, not just yes/no

---

## 🗂 Project Structure
capstone/
├── backend/
│ ├── main.py # FastAPI routes
│ ├── model.py # ML predictions
│ ├── explain.py # SHAP explainability
│ ├── credibility.py # Evidence credibility scoring
│ ├── nih_api.py # NIH PubMed client
│ ├── rag.py # FAISS + sentence-transformers
│ ├── llm.py # Gemini / Ollama / Template
│ ├── myhealthbox_api.py # Medicines + stockists
│ ├── diagnosis_mapper.py # Binary → specific condition
│ └── prescriptions.py # Patient portal
├── data/
│ └── dataset.csv # UCI Cleveland Heart Disease
├── models/
│ ├── tabpfn_model.pkl # Trained Random Forest
│ ├── decision_tree_model.pkl
│ └── metrics.json
└── frontend/ # React + Vite + Tailwind

---

## 🚀 Setup & Run Locally

### Prerequisites
- Python 3.11
- Node.js 18+
- Ollama (optional, for local LLM fallback)

### Backend

```bash
# Clone the repo
git clone https://github.com/Nithiasrisaravanan/aegis-cdss.git
cd aegis-cdss

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

# Start backend
uvicorn backend.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## 🧠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS, Axios |
| Backend | FastAPI, Uvicorn, Python 3.11 |
| ML Models | scikit-learn (Random Forest, Decision Tree) |
| Explainability | SHAP (TreeExplainer) |
| Evidence Retrieval | NIH PubMed E-utilities API |
| Vector Search | FAISS + sentence-transformers (all-MiniLM-L6-v2) |
| LLM | Gemini API → Ollama (Llama 3.2) → Template |
| Data | UCI Cleveland Heart Disease (Detrano et al., 1989) |

---

## 📊 Model Performance

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Random Forest | 86.7% | 88.46% | 82.14% | 85.19% | 93.75% |
| Decision Tree | 70.0% | 75.0% | 53.57% | 62.5% | 74.5% |

---

## 🆕 Novel Contribution

**Evidence-Validated Credibility Scoring** — For each top SHAP feature, the system queries PubMed live, computes cosine similarity between the feature-disease query and the retrieved abstract, and assigns a credibility percentage. Features with high SHAP impact but low literature support are flagged as potential spurious correlations. This cross-validation of ML reasoning against independent biomedical literature is not present in existing published CDSS prototypes.

---

## 📚 References

- Detrano R, et al. American Journal of Cardiology, 1989 (UCI Cleveland dataset)
- Lundberg SM, Lee SI. NeurIPS, 2017 (SHAP)
- Lewis P, et al. NeurIPS, 2020 (RAG)
- NIH PubMed E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/

---

## ⚠ Disclaimer

Aegis CDSS is a decision support tool only. All outputs are suggestions for a qualified clinician. The clinician makes the final diagnostic and treatment decisions.
