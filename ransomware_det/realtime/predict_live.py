import psutil
import time
import joblib
import numpy as np
import pandas as pd
import os
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
MODEL_PATH = "model/rf_model_session.pkl"
OUTPUT_DIR = "live_window_tests"

WINDOW_DURATION = 15      # seconds to observe system
SAMPLE_INTERVAL = 1.0     # seconds between raw snapshots

# =========================================================
# FEATURES (must match training exactly)
# =========================================================
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

# =========================================================
# SETUP
# =========================================================
os.makedirs(OUTPUT_DIR, exist_ok=True)

model = joblib.load(MODEL_PATH)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
RAW_LOG_PATH = os.path.join(OUTPUT_DIR, f"raw_window_{timestamp}.csv")
FEATURE_LOG_PATH = os.path.join(OUTPUT_DIR, f"feature_window_{timestamp}.csv")

previous_disk_writes = {}

print("\n" + "=" * 80)
print(" RAPPPTR LIVE WINDOW PREDICTOR")
print("=" * 80)
print(f"[INFO] Model Path       : {MODEL_PATH}")
print(f"[INFO] Window Duration  : {WINDOW_DURATION} sec")
print(f"[INFO] Sample Interval  : {SAMPLE_INTERVAL} sec")
print(f"[INFO] Raw Log Output   : {RAW_LOG_PATH}")
print(f"[INFO] Feature Output   : {FEATURE_LOG_PATH}")
print("=" * 80 + "\n")

# =========================================================
# PRIME CPU COUNTERS
# =========================================================
print("[INFO] Priming CPU counters...")
for proc in psutil.process_iter():
    try:
        proc.cpu_percent(interval=None)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

time.sleep(1)
print("[INFO] Starting capture...\n")

# =========================================================
# RAW COLLECTION
# =========================================================
raw_rows = []

start_time = time.time()

while time.time() - start_time < WINDOW_DURATION:
    snapshot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            pid = proc.info["pid"]
            name = proc.info["name"] or "unknown"

            cpu = proc.cpu_percent(interval=None)
            mem = proc.memory_percent()

            try:
                io = proc.io_counters()
                write_bytes = io.write_bytes if io else 0
            except (psutil.AccessDenied, AttributeError):
                write_bytes = 0

            key = (pid, name)

            if key not in previous_disk_writes:
                previous_disk_writes[key] = write_bytes
                delta = 0
            else:
                prev = previous_disk_writes[key]
                delta = max(0, write_bytes - prev)
                previous_disk_writes[key] = write_bytes

            raw_rows.append({
                "timestamp": snapshot_time,
                "pid": pid,
                "process_name": name,
                "cpu_percent": cpu,
                "memory_percent": mem,
                "disk_write_delta": delta
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(SAMPLE_INTERVAL)

# Save raw data
raw_df = pd.DataFrame(raw_rows)
raw_df.to_csv(RAW_LOG_PATH, index=False)

if raw_df.empty:
    print("[ERROR] No raw data captured.")
    exit()

# =========================================================
# FEATURE AGGREGATION (EXACTLY LIKE TRAINING)
# =========================================================
agg = raw_df.groupby("timestamp").agg(
    cpu_mean=("cpu_percent", "mean"),
    cpu_max=("cpu_percent", "max"),
    mem_mean=("memory_percent", "mean"),
    disk_write_sum=("disk_write_delta", "sum"),
    disk_write_max=("disk_write_delta", "max"),
    process_count=("pid", "count"),
    active_writers=("disk_write_delta", lambda x: (x > 0).sum())
).reset_index()

agg["disk_write_rate"] = agg["disk_write_sum"] / agg["active_writers"].clip(lower=1)

# Save all window feature rows
agg.to_csv(FEATURE_LOG_PATH, index=False)

# Use mean across the captured window for more stable classification
feature_vector = agg[FEATURE_COLS].mean()

X_live = np.array([[feature_vector[col] for col in FEATURE_COLS]], dtype=np.float64)

# =========================================================
# PREDICTION
# =========================================================
prob = float(model.predict_proba(X_live)[0][1])
pred = int(prob >= 0.50)

label = "RANSOMWARE 🚨" if pred == 1 else "BENIGN ✅"

print("\n" + "=" * 80)
print(" LIVE WINDOW RESULT")
print("=" * 80)
print(f"Prediction           : {label}")
print(f"Ransomware Probability: {prob:.3f}")
print("-" * 80)

for col in FEATURE_COLS:
    print(f"{col:18}: {feature_vector[col]:.3f}")

print("=" * 80)
print("[INFO] Capture complete.")
