# response/replay_realtime.py

import sys
import os
import time
import pandas as pd
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from response.hybrid_decision import hybrid_decision

SEQ_LEN = 30
SEQUENCE_DELAY = 1.0

print("[INFO] Loading processed feature rows...")

df = pd.read_csv("data/processed/labeled_features.csv")

print(f"[INFO] Loaded {len(df)} feature rows")
print("[INFO] Starting pseudo real-time hybrid detection...\n")

buffer = []

for idx, row in df.iterrows():

    buffer.append(row)

    if len(buffer) > SEQ_LEN:
        buffer.pop(0)

    if len(buffer) < SEQ_LEN:
        continue

    window_df = pd.DataFrame(buffer)

    timestamp = datetime.now().strftime("%H:%M:%S")

    rf_prob, lstm_score, decision, source = hybrid_decision(window_df)

    # SAFE formatting
    rf_display = f"{rf_prob:.3f}" if isinstance(rf_prob, (int, float)) else str(rf_prob)
    lstm_display = f"{lstm_score:.6f}" if isinstance(lstm_score, (int, float)) else str(lstm_score)

    print(
        f"[{timestamp}] "
        f"Step {idx:04d} | "
        f"RF Prob: {rf_display} | "
        f"LSTM: {lstm_display} | "
        f"Decision: {decision:<18} | "
        f"Triggered by: {source}"
    )

    time.sleep(SEQUENCE_DELAY)

print("\n[INFO] Real-time replay completed.")
