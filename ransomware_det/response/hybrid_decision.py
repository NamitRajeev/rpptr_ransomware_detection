import numpy as np
import joblib
from tensorflow.keras.models import load_model

# ----------------------------
# CONFIGURATION
# ----------------------------
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

SEQ_LEN = 30

RF_MODEL_PATH = "model/rf_model.pkl"
LSTM_MODEL_PATH = "lstm/lstm_model.h5"
SCALER_PATH = "data/processed/scaler.pkl"
BENIGN_ERR_PATH = "data/processed/benign_errors.npy"

# ----------------------------
# LOAD MODELS
# ----------------------------
rf_model = joblib.load(RF_MODEL_PATH)
lstm_model = load_model(LSTM_MODEL_PATH, compile=False)
scaler = joblib.load(SCALER_PATH)

# Derive LSTM threshold
benign_errors = np.load(BENIGN_ERR_PATH)
LSTM_THRESHOLD = benign_errors.mean() + 3 * benign_errors.std()

print("[INFO] Hybrid decision module initialized")
print(f"[INFO] LSTM anomaly threshold = {LSTM_THRESHOLD:.6f}")

# ----------------------------
# HYBRID DECISION FUNCTION
# ----------------------------
def hybrid_decision(feature_window_df):

    # ---------------- RF ----------------
    rf_probs = rf_model.predict_proba(
        feature_window_df[FEATURE_COLS]
    )

    rf_prob_last = rf_probs[-1][1]
    rf_pred_last = 1 if rf_prob_last > 0.5 else 0

    # ---------------- LSTM ----------------
    if len(feature_window_df) < SEQ_LEN:
        return {
            "decision": "INSUFFICIENT_DATA",
            "rf_prob": rf_prob_last,
            "lstm_score": None,
            "threshold": LSTM_THRESHOLD
        }

    X = feature_window_df[FEATURE_COLS].values
    X_scaled = scaler.transform(X)

    X_seq = X_scaled[-SEQ_LEN:].reshape(
        1, SEQ_LEN, len(FEATURE_COLS)
    )

    X_true = X_seq[:, -1, :]
    X_pred = lstm_model.predict(X_seq, verbose=0)

    lstm_score = np.mean((X_true - X_pred) ** 2)

    # ---------------- Decision Logic ----------------
    if rf_pred_last == 1:
        decision = "RANSOMWARE (RF)"
    elif lstm_score > LSTM_THRESHOLD:
        decision = "SUSPICIOUS (LSTM)"
    else:
        decision = "BENIGN"

    return {
        "decision": decision,
        "rf_prob": rf_prob_last,
        "lstm_score": lstm_score,
        "threshold": LSTM_THRESHOLD
    }

# ----------------------------
if __name__ == "__main__":
    print("[INFO] Hybrid module ready")
