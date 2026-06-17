import pandas as pd
import numpy as np

np.random.seed(42)
n = 800

age = np.random.randint(29, 77, n)
sex = np.random.randint(0, 2, n)
cp = np.random.randint(0, 4, n)
trestbps = np.random.randint(94, 200, n)
chol = np.random.randint(126, 564, n)
fbs = np.random.randint(0, 2, n)
restecg = np.random.randint(0, 3, n)
thalach = np.random.randint(71, 202, n)
exang = np.random.randint(0, 2, n)
oldpeak = np.round(np.random.uniform(0, 6.2, n), 1)
slope = np.random.randint(0, 3, n)
ca = np.random.randint(0, 4, n)
thal = np.random.randint(1, 4, n)

# Generate target with realistic correlations
score = (
    (age > 55).astype(int) * 1.5 +
    sex * 0.8 +
    (cp == 0).astype(int) * 1.2 +
    (trestbps > 140).astype(int) * 0.7 +
    (chol > 240).astype(int) * 0.5 +
    fbs * 0.4 +
    exang * 1.0 +
    (oldpeak > 2).astype(int) * 1.0 +
    ca * 0.8 +
    np.random.normal(0, 0.5, n)
)
target = (score > score.mean()).astype(int)

df = pd.DataFrame({
    'age': age, 'sex': sex, 'cp': cp, 'trestbps': trestbps,
    'chol': chol, 'fbs': fbs, 'restecg': restecg, 'thalach': thalach,
    'exang': exang, 'oldpeak': oldpeak, 'slope': slope, 'ca': ca,
    'thal': thal, 'target': target
})

df.to_csv('data/dataset.csv', index=False)
print(f"Dataset created: {len(df)} rows")
print(df['target'].value_counts())
print(df.head())