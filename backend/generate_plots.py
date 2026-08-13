import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import joblib
import shap
from sklearn.metrics import (roc_curve, auc, confusion_matrix, 
                              ConfusionMatrixDisplay)
from sklearn.model_selection import train_test_split
import os

# Load data and models
df = pd.read_csv('data/dataset.csv')
X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

rf = joblib.load('models/tabpfn_model.pkl')
dt = joblib.load('models/decision_tree_model.pkl')

os.makedirs('plots', exist_ok=True)

# ── 1. ROC CURVE ──────────────────────────────────
plt.figure(figsize=(8, 6))

for model, name, color in [
    (rf, 'Random Forest', 'blue'),
    (dt, 'Decision Tree', 'orange')
]:
    y_prob = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, color=color, lw=2,
             label=f'{name} (AUC = {roc_auc:.4f})')

plt.plot([0, 1], [0, 1], 'k--', lw=1)
plt.xlabel('False Positive Rate', fontsize=12)
plt.ylabel('True Positive Rate', fontsize=12)
plt.title('ROC Curve — Random Forest vs Decision Tree', fontsize=14)
plt.legend(loc='lower right', fontsize=11)
plt.tight_layout()
plt.savefig('plots/roc_curve.png', dpi=150)
plt.close()
print("✅ ROC Curve saved!")

# ── 2. CONFUSION MATRIX ───────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, model, name in [
    (axes[0], rf, 'Random Forest'),
    (axes[1], dt, 'Decision Tree')
]:
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=['No Disease', 'Heart Disease']
    )
    disp.plot(ax=ax, colorbar=False, cmap='Blues')
    ax.set_title(f'Confusion Matrix — {name}', fontsize=13)

plt.tight_layout()
plt.savefig('plots/confusion_matrix.png', dpi=150)
plt.close()
print("✅ Confusion Matrix saved!")

# ── 3. SHAP SUMMARY PLOT ──────────────────────────
explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_test)

plt.figure(figsize=(10, 7))
if isinstance(shap_values, list):
    vals = shap_values[1]
else:
    if shap_values.ndim == 3:
        vals = shap_values[:, :, 1]
    else:
        vals = shap_values

shap.summary_plot(
    vals, X_test,
    plot_type='bar',
    show=False,
    plot_size=(10, 7)
)
plt.title('SHAP Feature Importance — Random Forest', fontsize=14)
plt.tight_layout()
plt.savefig('plots/shap_summary.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ SHAP Summary Plot saved!")

print("\n🎉 All plots saved in: capstone/plots/")
print("Files: roc_curve.png | confusion_matrix.png | shap_summary.png")