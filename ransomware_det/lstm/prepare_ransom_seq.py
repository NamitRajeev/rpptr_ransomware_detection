import pandas as pd
import numpy as np
import os
import joblib

INPUT_FILE = "data/processed/labeled_features.csv"
OUTPUT_DIR = "data/processed"
SEQ_LEN = 30

df = pd.read_csv(INPUT_FILE)
df = df[df["label"] == 1].reset_index(drop=True)

FEATURE_COLS = [
    "cpu_mean",
    "cpu_max",
    "mem_mean",
    "disk_write_sum",
    "disk_write_max",
    "process_count",
    "active_writers",
    "disk_write_rate"   # 🔴 NEW
]

X = df[FEATURE_COLS].values

scaler = joblib.load(os.path.join(OUTPUT_DIR, "scaler.pkl"))
X_scaled = scaler.transform(X)

X_sequences = []

for i in range(len(X_scaled) - SEQ_LEN):
    X_sequences.append(X_scaled[i:i+SEQ_LEN])

X_sequences = np.array(X_sequences)

np.save(os.path.join(OUTPUT_DIR, "X_ransomware_sequences.npy"), X_sequences)

print("[INFO] Ransomware sequence preparation completed")
print("X_ransomware shape:", X_sequences.shape)
