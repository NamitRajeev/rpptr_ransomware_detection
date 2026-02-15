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

from response.hybrid_decision import hybrid_decision


# -------------------------------------------------
# Configuration
# -------------------------------------------------
SEQ_LEN = 30
SEQUENCE_DELAY = 1.0   # 1 decision per second (examiner-friendly)

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

# -------------------------------------------------
# Load processed feature data (row-level, NOT sequences)
# -------------------------------------------------
print("[INFO] Loading processed feature rows...")

df = pd.read_csv("data/processed/labeled_features.csv")

print(f"[INFO] Loaded {len(df)} feature rows")
print("[INFO] Starting pseudo real-time hybrid detection...\n")


# -------------------------------------------------
# Real-time replay loop
# -------------------------------------------------
buffer = []

for idx, row in df.iterrows():

    # Add new row to rolling buffer
    buffer.append(row)

    # Keep only last SEQ_LEN rows
    if len(buffer) > SEQ_LEN:
        buffer.pop(0)

    # Only start detection once buffer is full
    if len(buffer) < SEQ_LEN:
        continue

    # Convert buffer to DataFrame
    window_df = pd.DataFrame(buffer)

    timestamp = datetime.now().strftime("%H:%M:%S")

    decision, source = hybrid_decision(window_df)

    print(
        f"[{timestamp}] "
        f"Step {idx:04d} | "
        f"Decision: {decision:<12} | "
        f"Triggered by: {source}"
    )

    time.sleep(SEQUENCE_DELAY)


print("\n[INFO] Real-time replay completed.")
