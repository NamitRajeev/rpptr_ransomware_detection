import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# ================= PATH SETUP =================

# This file is inside: ransomware_det/plots/
# So project root is one level up
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BASE_DIR)   # ransomware_det/

# LSTM artifacts
SEQS_DIR = os.path.join(BASE_DIR, "lstm", "seqs")

X_PATH = os.path.join(SEQS_DIR, "X_sequences.npy")
Y_PATH = os.path.join(SEQS_DIR, "y_sequences.npy")
MODEL_PATH = os.path.join(BASE_DIR, "lstm", "lstm_model.h5")

# ================= LOAD DATA =================

print("[INFO] Loading data and model...")

if not os.path.exists(X_PATH):
    raise FileNotFoundError(f"Missing file: {X_PATH}")

if not os.path.exists(Y_PATH):
    raise FileNotFoundError(f"Missing file: {Y_PATH}")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Missing file: {MODEL_PATH}")

X = np.load(X_PATH)
y = np.load(Y_PATH)

model = load_model(MODEL_PATH, compile=False)

# ================= RECONSTRUCTION ERROR =================

print("[INFO] Computing reconstruction error...")
X_recon = model.predict(X, verbose=0)

# Feature order:
# 0 avg_cpu
# 1 max_cpu
# 2 avg_memory
# 3 total_disk_write
# 4 max_write_burst
# 5 process_lifetime

FEATURE_WEIGHTS = np.array([1.0, 1.0, 1.0, 3.0, 3.0, 1.0])

errors = np.mean(
    np.square((X - X_recon) * FEATURE_WEIGHTS),
    axis=(1, 2)
)

benign_errors = errors[y == 0]
ransomware_errors = errors[y == 1]

threshold = benign_errors.mean() + 2 * benign_errors.std()

# ================= PLOT =================

plt.figure(figsize=(8, 5))

plt.hist(benign_errors, bins=20, alpha=0.7, label="Benign")
plt.hist(ransomware_errors, bins=20, alpha=0.7, label="Ransomware-like")

plt.axvline(
    threshold,
    linestyle="--",
    linewidth=2,
    label="Anomaly Threshold"
)

plt.xlabel("Reconstruction Error")
plt.ylabel("Number of Sequences")
plt.title("LSTM Anomaly Score Distribution")
plt.legend()
plt.tight_layout()

plt.show()
