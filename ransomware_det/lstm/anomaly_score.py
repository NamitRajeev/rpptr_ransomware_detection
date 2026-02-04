import os
import numpy as np
from tensorflow.keras.models import load_model

# ================= PATH SETUP =================

# Project root: ransomware_det/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEQS_DIR = os.path.join(BASE_DIR, "lstm", "seqs")

X_PATH = os.path.join(SEQS_DIR, "X_sequences.npy")
Y_PATH = os.path.join(SEQS_DIR, "y_sequences.npy")

MODEL_PATH = os.path.join(BASE_DIR, "lstm", "lstm_model.h5")

# ================= LOAD DATA =================

print("[INFO] Loading sequences and model...")

if not (os.path.exists(X_PATH) and os.path.exists(Y_PATH)):
    raise FileNotFoundError("Sequence files not found in lstm/seqs/")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("LSTM model not found")

X = np.load(X_PATH)
y = np.load(Y_PATH)

model = load_model(MODEL_PATH, compile=False)

print("[INFO] X shape:", X.shape)
print("[INFO] y shape:", y.shape)

# ================= RECONSTRUCTION =================

print("[INFO] Reconstructing sequences...")
X_recon = model.predict(X, verbose=0)

# ================= ANOMALY SCORE =================
# Mean Squared Error per sequence

reconstruction_error = np.mean(
    np.square(X - X_recon),
    axis=(1, 2)
)

# ================= SEPARATE BY LABEL =================

benign_errors = reconstruction_error[y == 0]
ransomware_errors = reconstruction_error[y == 1]

# ================= RESULTS =================

print("\n========== ANOMALY SCORE RESULTS ==========")

print(f"Total sequences: {len(reconstruction_error)}")

print("\nBenign sequences:")
print(f"  Count: {len(benign_errors)}")
print(f"  Mean reconstruction error: {benign_errors.mean():.6f}")
print(f"  Std deviation: {benign_errors.std():.6f}")

print("\nRansomware-like sequences:")
print(f"  Count: {len(ransomware_errors)}")
print(f"  Mean reconstruction error: {ransomware_errors.mean():.6f}")
print(f"  Std deviation: {ransomware_errors.std():.6f}")

# ================= OPTIONAL THRESHOLD =================

threshold = benign_errors.mean() + 2 * benign_errors.std()

print("\nSuggested anomaly threshold:")
print(f"  Threshold = {threshold:.6f}")

flagged = np.sum(reconstruction_error > threshold)

print(f"\nSequences flagged as anomalous: {flagged}/{len(reconstruction_error)}")
print("==========================================")
