# response/live_det.py

import sys
import os
import time
import joblib
import numpy as np
import pandas as pd
from collections import deque
from datetime import datetime
from tensorflow.keras.models import load_model

# -------------------------------------------------
# Project Path Setup
# -------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from lstm import anomaly_score as as_module
from lstm.anomaly_score import anomaly_score, is_anomalous

# -------------------------------------------------
# Configuration
# -------------------------------------------------
SEQ_LEN = 30
POLL_INTERVAL = 1.0
CONFIRM_WINDOW = 5
CONFIRM_COUNT = 2

LOG_PATH = os.path.join(PROJECT_ROOT, "data", "live_process_log.csv")

RF_FEATURE_ORDER = [
    'cpu_mean',
    'cpu_max',
    'mem_mean',
    'disk_write_sum',
    'disk_write_max',
    'process_count',
    'active_writers',
    'disk_write_rate'
]

# -------------------------------------------------
# Load Models + Scaler
# -------------------------------------------------
print("[INFO] Loading models...")

rf_model = joblib.load(os.path.join(PROJECT_ROOT, "model", "rf_model.pkl"))
lstm_model = load_model(os.path.join(PROJECT_ROOT, "lstm", "lstm_model.h5"), compile=False)
scaler = joblib.load(os.path.join(PROJECT_ROOT, "data", "processed", "scaler.pkl"))

print("[INFO] RF model loaded")
print("[INFO] LSTM model loaded")
print("[INFO] Threshold at runtime:", as_module.ANOMALY_THRESHOLD)
print("[INFO] Live detection engine started...\n")

# -------------------------------------------------
# Rolling Buffers
# -------------------------------------------------
sequence_buffer = deque(maxlen=SEQ_LEN)
anomaly_history = deque(maxlen=CONFIRM_WINDOW)

# -------------------------------------------------
# Feature Aggregation
# -------------------------------------------------
def aggregate_features(df):

    return {
        'cpu_mean': df["cpu_percent"].mean(),
        'cpu_max': df["cpu_percent"].max(),
        'mem_mean': df["memory_percent"].mean(),
        'disk_write_sum': df["disk_write_delta"].sum(),
        'disk_write_max': df["disk_write_delta"].max(),
        'process_count': df["pid"].nunique(),
        'active_writers': (df["disk_write_delta"] > 0).sum(),
        'disk_write_rate': df["disk_write_delta"].sum() / max(len(df), 1)
    }

# -------------------------------------------------
# Live Detection Loop
# -------------------------------------------------
while True:
    try:

        if not os.path.exists(LOG_PATH):
            time.sleep(POLL_INTERVAL)
            continue

        df = pd.read_csv(LOG_PATH)

        if len(df) < 50:
            time.sleep(POLL_INTERVAL)
            continue

        latest_df = df.tail(50)

        feature_row = aggregate_features(latest_df)

        sequence_buffer.append(feature_row)

        if len(sequence_buffer) == SEQ_LEN:

            window_df = pd.DataFrame(sequence_buffer)

            # =====================================================
            # 🔵 FIXED RF INPUT (30-second summary instead of 1 row)
            # =====================================================
            rf_summary = window_df[RF_FEATURE_ORDER].mean().to_frame().T
            rf_prob = rf_model.predict_proba(rf_summary)[0][1]
            rf_pred = 1 if rf_prob >= 0.5 else 0

            # -------------------------
            # LSTM (UNCHANGED)
            # -------------------------
            sequence = window_df[RF_FEATURE_ORDER].values
            sequence_scaled = scaler.transform(sequence)

            recon_error = anomaly_score(lstm_model, sequence_scaled)
            current_flag = is_anomalous(recon_error)

            anomaly_history.append(current_flag)
            confirmed_anomaly = sum(anomaly_history) >= CONFIRM_COUNT

            # -------------------------
            # HYBRID DECISION
            # -------------------------
            if rf_pred == 1 or confirmed_anomaly:
                decision = "🚨 RANSOMWARE DETECTED 🚨"
            else:
                decision = "BENIGN"

            timestamp = datetime.now().strftime("%H:%M:%S")

            print(
                f"[{timestamp}] "
                f"RF:{rf_pred} (p={rf_prob:.3f}) | "
                f"LSTM:{recon_error:.6f} | "
                f"Confirmed:{confirmed_anomaly} | "
                f"{decision}"
            )

        time.sleep(POLL_INTERVAL)

    except Exception as e:
        print("[ERROR]", e)
        time.sleep(POLL_INTERVAL)
