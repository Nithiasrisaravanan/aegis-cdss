import pandas as pd
import numpy as np
import json
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

df = pd.read_csv('data/dataset.csv')
X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"Train: {len(X_train)} | Test: {len(X_test)}")

def evaluate(model, X_test, y_test, name):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = {
        "model": name,
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall":    round(recall_score(y_test, y_pred), 4),
        "f1":        round(f1_score(y_test, y_pred), 4),
        "roc_auc":   round(roc_auc_score(y_test, y_prob), 4)
    }
    print(f"\n{name} Results:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    return metrics

print("\nTraining Random Forest (Primary)...")
rf = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=8)
rf.fit(X_train, y_train)
rf_metrics = evaluate(rf, X_test, y_test, "RandomForest")
joblib.dump(rf, 'models/tabpfn_model.pkl')
print("Random Forest saved!")

print("\nTraining Decision Tree (Baseline)...")
dt = DecisionTreeClassifier(random_state=42, max_depth=5)
dt.fit(X_train, y_train)
dt_metrics = evaluate(dt, X_test, y_test, "DecisionTree")
joblib.dump(dt, 'models/decision_tree_model.pkl')
print("Decision Tree saved!")

metrics = {
    "primary": rf_metrics,
    "decision_tree": dt_metrics,
    "test_size": len(X_test),
    "train_size": len(X_train),
    "features": list(X.columns)
}
with open('models/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print("\nmetrics.json saved!")
print("\nTraining complete!")
