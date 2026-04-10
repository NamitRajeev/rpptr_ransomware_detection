import psutil
import time
import joblib
import numpy as np
import pandas as pd
import os
from collections import deque
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
MODEL_PATH = "model/rf_model_session.pkl"
LOG_DIR = "live_logs"

RAW_SAMPLE_INTERVAL = 1.0     # how often to collect raw process snapshots
WINDOW_DURATION = 10          # seconds of raw data per prediction window
PROB_THRESHOLD = 0.55         # slightly lower for demo sensitivity
ROLLING_WINDOW = 3            # rolling prediction smoothing
ALERT_MIN_HITS = 2            # if >=2 of last 3 are ransomware -> alert
PRINT_FEATURES = True

# =========================================================
# FEATURES (MUST MATCH TRAINING)
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
os.makedirs(LOG_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_PATH = os.path.join(LOG_DIR, f"buffered_live_log_{timestamp}.csv")

model = joblib.load(MODEL_PATH)

print("\n" + "=" * 80)
print(" RAPPPTR BUFFERED LIVE DETECTOR")
print("=" * 80)
print(f"[INFO] Model Path            : {MODEL_PATH}")
print(f"[INFO] Log File              : {LOG_PATH}")
print(f"[INFO] Raw Sample Interval   : {RAW_SAMPLE_INTERVAL} sec")
print(f"[INFO] Window Duration       : {WINDOW_DURATION} sec")
print(f"[INFO] Prob Threshold        : {PROB_THRESHOLD}")
print(f"[INFO] Stable Alert Rule     : {ALERT_MIN_HITS}/{ROLLING_WINDOW}")
print("=" * 80 + "\n")

previous_disk_writes = {}
history = []
rolling_preds = deque(maxlen=ROLLING_WINDOW)

start_time = datetime.now()
window_count = 0

# Prime CPU counters
print("[INFO] Priming CPU counters...")
for proc in psutil.process_iter():
    try:
        proc.cpu_percent(interval=None)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

time.sleep(1)
print("[INFO] Detector started.\n")

def collect_raw_snapshot():
    rows = []

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

            rows.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pid": pid,
                "process_name": name,
                "cpu_percent": cpu,
                "memory_percent": mem,
                "disk_write_delta": delta
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return rows

def aggregate_window(raw_df):
    if raw_df.empty:
        return None

    # EXACTLY LIKE TRAINING FEATURE EXTRACTOR
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

    # Use the LAST aggregated row from this buffered window
    return agg.iloc[-1]

try:
    while True:
        print("\n[INFO] Collecting raw window...")
        raw_rows = []

        window_start = time.time()
        while time.time() - window_start < WINDOW_DURATION:
            raw_rows.extend(collect_raw_snapshot())
            time.sleep(RAW_SAMPLE_INTERVAL)

        raw_df = pd.DataFrame(raw_rows)

        if raw_df.empty:
            print("[WARN] No raw data collected in this window.")
            continue

        feature_row = aggregate_window(raw_df)
        if feature_row is None:
            print("[WARN] Failed to aggregate features.")
            continue

        features = np.array([[
            feature_row["cpu_mean"],
            feature_row["cpu_max"],
            feature_row["mem_mean"],
            feature_row["disk_write_sum"],
            feature_row["disk_write_max"],
            feature_row["process_count"],
            feature_row["active_writers"],
            feature_row["disk_write_rate"]
        ]], dtype=np.float64)

        prob = float(model.predict_proba(features)[0][1])
        instant_pred = 1 if prob >= PROB_THRESHOLD else 0

        rolling_preds.append(instant_pred)
        stable_pred = 1 if sum(rolling_preds) >= ALERT_MIN_HITS else 0

        status = "RANSOMWARE 🚨" if stable_pred == 1 else "BENIGN ✅"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = {
            "timestamp": now,
            "cpu_mean": float(feature_row["cpu_mean"]),
            "cpu_max": float(feature_row["cpu_max"]),
            "mem_mean": float(feature_row["mem_mean"]),
            "disk_write_sum": float(feature_row["disk_write_sum"]),
            "disk_write_max": float(feature_row["disk_write_max"]),
            "process_count": int(feature_row["process_count"]),
            "active_writers": int(feature_row["active_writers"]),
            "disk_write_rate": float(feature_row["disk_write_rate"]),
            "ransomware_probability": prob,
            "instant_prediction": instant_pred,
            "stable_prediction": stable_pred,
            "rolling_hits": int(sum(rolling_preds))
        }

        history.append(row)

        print("=" * 80)
        print(f"[{now}] {status}")
        print(f"  Instant Prob      : {prob:.3f}")
        print(f"  Rolling Hits      : {sum(rolling_preds)}/{ROLLING_WINDOW}")
        print(f"  Instant Pred      : {'RANSOMWARE' if instant_pred else 'BENIGN'}")
        print(f"  Stable Pred       : {'RANSOMWARE' if stable_pred else 'BENIGN'}")

        if PRINT_FEATURES:
            print(f"  cpu_mean          : {row['cpu_mean']:.3f}")
            print(f"  cpu_max           : {row['cpu_max']:.3f}")
            print(f"  mem_mean          : {row['mem_mean']:.3f}")
            print(f"  disk_write_sum    : {row['disk_write_sum']:.0f}")
            print(f"  disk_write_max    : {row['disk_write_max']:.0f}")
            print(f"  process_count     : {row['process_count']}")
            print(f"  active_writers    : {row['active_writers']}")
            print(f"  disk_write_rate   : {row['disk_write_rate']:.0f}")

except KeyboardInterrupt:
    df = pd.DataFrame(history)
    df.to_csv(LOG_PATH, index=False)

    print("\n" + "=" * 80)
    print("[INFO] BUFFERED LIVE DETECTOR INTERRUPTED")
    print("=" * 80)
    print(f"Start Time            : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time              : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Windows         : {len(history)}")
    print(f"CSV Log Saved         : {LOG_PATH}")

    if len(df) > 0:
        print("\n[SUMMARY STATS]")
        print(df[[
            "ransomware_probability",
            "disk_write_sum",
            "disk_write_max",
            "active_writers",
            "disk_write_rate",
            "process_count"
        ]].describe().round(3))

        if int(df["stable_prediction"].sum()) > 0:
            print("\n[SUMMARY] Stable ransomware-like behavior WAS detected.")
        else:
            print("\n[SUMMARY] No stable ransomware detection occurred.")
    else:
        print("[WARN] No data captured.")

    print("=" * 80)
