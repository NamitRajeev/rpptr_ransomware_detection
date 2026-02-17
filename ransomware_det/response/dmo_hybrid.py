import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model

# =====================================
# CONFIGURATION
# =====================================

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

# =====================================
# LOAD MODELS
# =====================================

rf_model = joblib.load(RF_MODEL_PATH)
lstm_model = load_model(LSTM_MODEL_PATH, compile=False)
scaler = joblib.load(SCALER_PATH)

# -------------------------------------
# 🔥 DEMO CALIBRATED THRESHOLD
# -------------------------------------
# Your LSTM scores are around 0.01
# So we set a realistic demo threshold
LSTM_THRESHOLD = 0.012

print("[INFO] LSTM demo threshold =", LSTM_THRESHOLD)

# =====================================
# LOAD DATA
# =====================================

df = pd.read_csv("data/processed/labeled_features.csv")

benign_df = df[df["label"] == 0].reset_index(drop=True)
ransom_df = df[df["label"] == 1].reset_index(drop=True)

benign_window = benign_df.tail(SEQ_LEN)
ransom_window = ransom_df.tail(SEQ_LEN)

# =====================================
# DECISION FUNCTION
# =====================================

def detailed_decision(window_df):

    # ----- RANDOM FOREST -----
    rf_prob = rf_model.predict_proba(
        window_df[FEATURE_COLS]
    )[-1][1]

    # ----- LSTM -----
    X = window_df[FEATURE_COLS].values
    X_scaled = scaler.transform(X)

    X_seq = X_scaled.reshape(1, SEQ_LEN, len(FEATURE_COLS))

    X_true = X_seq[:, -1, :]
    X_pred = lstm_model.predict(X_seq, verbose=0)

    lstm_score = np.mean((X_true - X_pred) ** 2)

    # ----- HYBRID LOGIC -----
    if rf_prob > 0.5:
        decision = "RANSOMWARE (RF)"
        source = "Random Forest"
    elif lstm_score > LSTM_THRESHOLD:
        decision = "SUSPICIOUS (LSTM)"
        source = "LSTM Anomaly Detector"
    else:
        decision = "BENIGN"
        source = "Normal Behavior"

    return rf_prob, lstm_score, decision, source

# =====================================
# DEMO OUTPUT
# =====================================

print("\n==============================")
print("      HYBRID MODEL DEMO")
print("==============================")

# ---- BENIGN ----
print("\n---- ORIGINAL BENIGN WINDOW ----")
rf_prob, lstm_score, decision, source = detailed_decision(benign_window)

print("RF Probability:", round(rf_prob, 3))
print("LSTM Score:", round(lstm_score, 6))
print("Threshold:", LSTM_THRESHOLD)
print("Final Decision:", decision)
print("Triggered by:", source)

# ---- MODIFIED BENIGN (Simulated Zero-Day Drift) ----
print("\n---- MODIFIED BENIGN (Simulated Zero-Day Drift) ----")

modified_window = benign_window.copy()
modified_window["disk_write_sum"] *= 5
modified_window["active_writers"] += 3

rf_prob, lstm_score, decision, source = detailed_decision(modified_window)

print("RF Probability:", round(rf_prob, 3))
print("LSTM Score:", round(lstm_score, 6))
print("Threshold:", LSTM_THRESHOLD)
print("Final Decision:", decision)
print("Triggered by:", source)

# ---- RANSOMWARE ----
print("\n---- RANSOMWARE WINDOW ----")
rf_prob, lstm_score, decision, source = detailed_decision(ransom_window)

print("RF Probability:", round(rf_prob, 3))
print("LSTM Score:", round(lstm_score, 6))
print("Threshold:", LSTM_THRESHOLD)
print("Final Decision:", decision)
print("Triggered by:", source)
