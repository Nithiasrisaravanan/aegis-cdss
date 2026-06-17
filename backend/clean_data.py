import pandas as pd
import numpy as np

# UCI Cleveland raw file has no headers and uses ? for missing values
cols = ['age','sex','cp','trestbps','chol','fbs','restecg',
        'thalach','exang','oldpeak','slope','ca','thal','target']

df = pd.read_csv('data/processed.cleveland.data', 
                  header=None, 
                  names=cols, 
                  na_values='?')

print(f"Raw rows: {len(df)}")
print(f"Missing values:\n{df.isnull().sum()}")

# Drop rows with missing values (only 6 rows affected)
df = df.dropna()

# Convert target to binary (0 = no disease, 1 = disease present)
df['target'] = (df['target'] > 0).astype(int)

# Ensure correct dtypes
df['ca'] = df['ca'].astype(int)
df['thal'] = df['thal'].astype(int)

print(f"\nCleaned rows: {len(df)}")
print(f"Target distribution:\n{df['target'].value_counts()}")
print(f"\nSample:\n{df.head()}")

# Save as our official dataset
df.to_csv('data/dataset.csv', index=False)
print("\n✅ dataset.csv saved successfully!")