import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
from sklearn.preprocessing import StandardScaler

SEQ_LEN = 30

FEATURE_COLS = [
    "cpu_mean",
    "cpu_max",
    "mem_mean",
    "disk_write_sum",
    "disk_write_max",
    "process_count",
    "active_writers",
    "disk_write_rate"
]

print("[INFO] Loading model...")
model = load_model("lstm/lstm_model.h5", compile=False)

print("[INFO] Loading scaler...")
scaler = joblib.load("data/processed/scaler.pkl")

print("[INFO] Loading labeled data...")
df = pd.read_csv("data/processed/labeled_features.csv")

# Separate benign and ransomware
df_benign = df[df["label"] == 0]
df_ransom = df[df["label"] == 1]

def build_sequences(df_part):
    X_raw = df_part[FEATURE_COLS].values
    X_scaled = scaler.transform(X_raw)

    sequences = []
    for i in range(len(X_scaled) - SEQ_LEN):
        sequences.append(X_scaled[i:i + SEQ_LEN])

    return np.array(sequences)

print("[INFO] Building benign sequences...")
X_benign = build_sequences(df_benign)

print("[INFO] Building ransomware sequences...")
X_ransom = build_sequences(df_ransom)

def compute_errors(X):
    X_pred = model.predict(X, verbose=0)
    errors = np.mean((X - X_pred) ** 2, axis=(1, 2))
    return errors


print("[INFO] Computing reconstruction errors...")

benign_errors = compute_errors(X_benign)
ransom_errors = compute_errors(X_ransom)

print("\n========== LSTM EVALUATION ==========\n")

print(f"Benign mean error: {benign_errors.mean():.6f}")
print(f"Ransom mean error: {ransom_errors.mean():.6f}")

print(f"Benign std: {benign_errors.std():.6f}")
print(f"Ransom std: {ransom_errors.std():.6f}")

threshold = benign_errors.mean() + 3 * benign_errors.std()
print(f"Threshold (μ + 3σ): {threshold:.6f}")

ransom_detected = np.sum(ransom_errors > threshold)

print(f"\nRansom sequences above threshold: {ransom_detected}/{len(ransom_errors)}")
print(f"Detection rate: {(ransom_detected/len(ransom_errors))*100:.2f}%")
