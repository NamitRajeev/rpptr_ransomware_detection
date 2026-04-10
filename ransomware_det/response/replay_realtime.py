# response/replay_realtime.py

import sys
import os
import time
import pandas as pd
from datetime import datetime

# -------------------------------------------------
# Ensure project root is in Python path
# -------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

sys.path.append(os.path.dirname(__file__))

from hybrid_decision import hybrid_decision


# -------------------------------------------------
# Configuration
# -------------------------------------------------
SEQ_LEN = 30
SEQUENCE_DELAY = 0.7   # smooth demo speed

# -------------------------------------------------
# Load processed feature data
# -------------------------------------------------
print("[INFO] Loading processed feature rows...")

df = pd.read_csv("data/processed/labeled_features.csv")

# 🔥 Shuffle dataset for realistic replay
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"[INFO] Loaded {len(df)} feature rows")
print("[INFO] Starting pseudo real-time hybrid detection...\n")

# -------------------------------------------------
# Replay loop
# -------------------------------------------------
buffer = []
correct = 0
total = 0

for idx, row in df.iterrows():

    buffer.append(row)

    if len(buffer) > SEQ_LEN:
        buffer.pop(0)

    if len(buffer) < SEQ_LEN:
        continue

    window_df = pd.DataFrame(buffer)

    timestamp = datetime.now().strftime("%H:%M:%S")

    # Get full detailed decision
    rf_prob, lstm_score, decision, source = hybrid_decision(window_df)


    # Convert decision to numeric
    predicted_label = 1 if "RANSOMWARE" in decision else 0
    true_label = int(row["label"])

    total += 1
    if predicted_label == true_label:
        correct += 1

    accuracy = correct / total

    print(
        f"[{timestamp}] "
        f"Step {idx:04d} | "
        #f"True: {true_label} | "
        f"RF Prob: {rf_prob:.3f} | "
        f"LSTM: {lstm_score:.4f} | "
        f"Decision: {decision:<18} | "
        f"Acc: {accuracy:.3f}"
    )

    time.sleep(SEQUENCE_DELAY)

print("\n[INFO] Replay completed.")
