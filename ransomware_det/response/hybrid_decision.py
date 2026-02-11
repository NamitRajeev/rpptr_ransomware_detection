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
# LOAD MODELS & PARAMETERS
# ----------------------------
rf_model = joblib.load(RF_MODEL_PATH)
lstm_model = load_model(LSTM_MODEL_PATH, compile=False)
scaler = joblib.load(SCALER_PATH)

# Dynamically derive threshold
benign_errors = np.load(BENIGN_ERR_PATH)
LSTM_THRESHOLD = benign_errors.mean() + 3 * benign_errors.std()

print("[INFO] Hybrid decision module initialized")
print(f"[INFO] LSTM anomaly threshold = {LSTM_THRESHOLD:.6f}")

# ----------------------------
# HYBRID DECISION FUNCTION
# ----------------------------
def hybrid_decision(feature_window_df):
    """
    Parameters:
        feature_window_df : pandas.DataFrame
            Last SEQ_LEN rows of extracted features

    Returns:
        decision (str)
        confidence_source (str)
    """

    # --------- Random Forest (Supervised) ----------
    rf_pred = rf_model.predict(
        feature_window_df[FEATURE_COLS]
    )[-1]

    if rf_pred == 1:
        return "RANSOMWARE", "Random Forest (Supervised)"

    # --------- LSTM Anomaly Detection ----------
    if len(feature_window_df) < SEQ_LEN:
        return "INSUFFICIENT_DATA", "Waiting for sequence"

    X = feature_window_df[FEATURE_COLS].values
    X_scaled = scaler.transform(X)

    X_seq = X_scaled[-SEQ_LEN:].reshape(
        1, SEQ_LEN, len(FEATURE_COLS)
    )

    X_true = X_seq[:, -1, :]
    X_pred = lstm_model.predict(X_seq, verbose=0)

    anomaly_score = np.mean((X_true - X_pred) ** 2)

    if anomaly_score > LSTM_THRESHOLD:
        return "SUSPICIOUS", "LSTM Anomaly Detector"

    return "BENIGN", "Normal behavior"

# ----------------------------
# MODULE READY
# ----------------------------
if __name__ == "__main__":
    print("[INFO] Hybrid module ready for integration")
    print("Use hybrid_decision(feature_window_df) in monitoring pipeline")
