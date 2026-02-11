import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler
import joblib

INPUT_FILE = "data/processed/labeled_features.csv"
OUTPUT_DIR = "data/processed"
SEQ_LEN = 30

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(INPUT_FILE)

# 🔴 BENIGN ONLY
df = df[df["label"] == 0].reset_index(drop=True)

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

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

joblib.dump(scaler, os.path.join(OUTPUT_DIR, "scaler.pkl"))

X_sequences = []
y_sequences = []

for i in range(len(X_scaled) - SEQ_LEN):
    X_sequences.append(X_scaled[i:i+SEQ_LEN])
    y_sequences.append(0)

np.save(os.path.join(OUTPUT_DIR, "X_sequences.npy"), np.array(X_sequences))
np.save(os.path.join(OUTPUT_DIR, "y_sequences.npy"), np.array(y_sequences))

print("[INFO] LSTM sequence preparation completed")
print("X shape:", np.array(X_sequences).shape)
