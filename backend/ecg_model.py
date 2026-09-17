import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECG_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'ecg_cnn_model.pth')

# ── 1. Dataset ────────────────────────────────────────────────────────────────
class ECGDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32).unsqueeze(1)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# ── 2. 1D CNN Model ───────────────────────────────────────────────────────────
class ECG_CNN(nn.Module):
    def __init__(self, num_classes=5):
        super(ECG_CNN, self).__init__()
        self.conv_block = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=5, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),

            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),

            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 23, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.conv_block(x)
        x = self.classifier(x)
        return x

# ── 3. Train ──────────────────────────────────────────────────────────────────
def train_ecg_model():
    print("Loading ECG data...")
    train_path = os.path.join(BASE_DIR, 'data', 'ecg', 'mitbih_train.csv')
    test_path = os.path.join(BASE_DIR, 'data', 'ecg', 'mitbih_test.csv')

    train_df = pd.read_csv(train_path, header=None)
    test_df = pd.read_csv(test_path, header=None)

    X_train = train_df.iloc[:, :-1].values.astype(np.float32)
    y_train = train_df.iloc[:, -1].values.astype(np.int64)
    X_test = test_df.iloc[:, :-1].values.astype(np.float32)
    y_test = test_df.iloc[:, -1].values.astype(np.int64)

    print(f"Train: {len(X_train)} | Test: {len(X_test)}")
    print(f"Classes: {np.unique(y_train)}")

    # Use subset for faster training
    subset = 20000
    idx = np.random.choice(len(X_train), subset, replace=False)
    X_train = X_train[idx]
    y_train = y_train[idx]

    train_dataset = ECGDataset(X_train, y_train)
    test_dataset = ECGDataset(X_test, y_test)
    train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    model = ECG_CNN(num_classes=5).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)

    print("\nTraining ECG CNN...")
    for epoch in range(10):
        model.train()
        total_loss = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            output = model(X_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        scheduler.step()
        print(f"Epoch {epoch+1}/10 | Loss: {total_loss/len(train_loader):.4f}")

    # Evaluate
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(device)
            output = model(X_batch)
            preds = torch.argmax(output, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(y_batch.numpy())

    acc = accuracy_score(all_labels, all_preds)
    print(f"\nECG CNN Test Accuracy: {acc:.4f}")
    print(classification_report(all_labels, all_preds,
          target_names=['Normal', 'Supraventricular', 'Ventricular', 'Fusion', 'Unknown']))

    torch.save(model.state_dict(), ECG_MODEL_PATH)
    print(f"✅ ECG CNN model saved to {ECG_MODEL_PATH}")
    return model, acc

# ── 4. Inference ──────────────────────────────────────────────────────────────
def load_ecg_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = ECG_CNN(num_classes=5).to(device)
    model.load_state_dict(torch.load(ECG_MODEL_PATH, map_location=device))
    model.eval()
    return model, device

def predict_ecg(ecg_signal: list) -> dict:
    """
    ecg_signal: list of 187 float values representing one ECG beat
    Returns: predicted class, probabilities, cardiac risk score
    """
    try:
        model, device = load_ecg_model()
        signal = np.array(ecg_signal, dtype=np.float32)
        signal = signal[:187] if len(signal) >= 187 else np.pad(signal, (0, 187 - len(signal)))
        tensor = torch.tensor(signal).unsqueeze(0).unsqueeze(0).to(device)

        with torch.no_grad():
            output = model(tensor)
            probs = torch.softmax(output, dim=1).cpu().numpy()[0]
            pred_class = int(np.argmax(probs))

        CLASS_LABELS = ['Normal', 'Supraventricular', 'Ventricular', 'Fusion', 'Unknown']
        RISK_WEIGHTS = [0.0, 0.4, 0.8, 0.6, 0.3]

        ecg_risk_score = float(sum(probs[i] * RISK_WEIGHTS[i] for i in range(5)))

        return {
            "ecg_class": CLASS_LABELS[pred_class],
            "ecg_class_id": pred_class,
            "ecg_probabilities": {CLASS_LABELS[i]: round(float(probs[i]), 4) for i in range(5)},
            "ecg_risk_score": round(ecg_risk_score * 100, 1),
            "ecg_available": True
        }
    except Exception as e:
        return {
            "ecg_class": "Unavailable",
            "ecg_risk_score": 0.0,
            "ecg_available": False,
            "error": str(e)
        }

# ── 5. Fusion ─────────────────────────────────────────────────────────────────
def fuse_predictions(tabular_prob: float, ecg_risk_score: float,
                     ecg_available: bool, weight_tabular: float = 0.7) -> dict:
    """
    Fuses tabular RF probability with ECG CNN risk score.
    Default: 70% tabular + 30% ECG
    """
    if not ecg_available:
        return {
            "fused_probability": round(tabular_prob * 100, 1),
            "fusion_used": False,
            "weights": {"tabular": 1.0, "ecg": 0.0}
        }

    weight_ecg = 1 - weight_tabular
    ecg_prob = ecg_risk_score / 100
    fused = (weight_tabular * tabular_prob) + (weight_ecg * ecg_prob)

    return {
        "fused_probability": round(fused * 100, 1),
        "fusion_used": True,
        "weights": {"tabular": weight_tabular, "ecg": weight_ecg},
        "tabular_contribution": round(tabular_prob * 100, 1),
        "ecg_contribution": round(ecg_prob * 100, 1)
    }

if __name__ == '__main__':
    train_ecg_model()