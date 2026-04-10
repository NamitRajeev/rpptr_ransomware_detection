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

INTERVAL = 2.0                 # must match your collection cadence as closely as possible
WARMUP_WINDOWS = 3             # ignore unstable first few windows
PROB_THRESHOLD = 0.60          # probability threshold for instant prediction
ROLLING_WINDOW = 5             # number of recent windows to remember
ALERT_MIN_HITS = 3             # if >= this many ransomware hits in rolling window -> alert
PRINT_FEATURES = True          # print live feature values
SAVE_ON_EVERY_LOOP = False     # set True only if you want ultra-safe logging (slower)

# =========================================================
# FEATURES (MUST MATCH TRAINING EXACTLY)
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
LOG_PATH = os.path.join(LOG_DIR, f"live_detector_log_{timestamp}.csv")

model = joblib.load(MODEL_PATH)

print("\n" + "=" * 80)
print(" RAPPPTR FINAL LIVE DETECTOR")
print("=" * 80)
print(f"[INFO] Model Path            : {MODEL_PATH}")
print(f"[INFO] Log File              : {LOG_PATH}")
print(f"[INFO] Interval              : {INTERVAL} sec")
print(f"[INFO] Warm-up Windows       : {WARMUP_WINDOWS}")
print(f"[INFO] Instant Prob Threshold: {PROB_THRESHOLD}")
print(f"[INFO] Stable Alert Rule     : {ALERT_MIN_HITS}/{ROLLING_WINDOW}")
print("=" * 80 + "\n")

# =========================================================
# STATE
# =========================================================
previous_disk_writes = {}
history = []
rolling_preds = deque(maxlen=ROLLING_WINDOW)

start_time = datetime.now()
window_count = 0
instant_ransom_hits = 0
stable_ransom_hits = 0
max_prob = 0.0
max_prob_timestamp = None

# =========================================================
# PRIME CPU COUNTERS
# =========================================================
print("[INFO] Priming CPU counters...")
for proc in psutil.process_iter():
    try:
        proc.cpu_percent(interval=None)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

time.sleep(1.0)
print("[INFO] Detector started.\n")

# =========================================================
# MAIN LOOP
# =========================================================
try:
    while True:
        loop_start = time.time()

        cpu_vals = []
        mem_vals = []
        write_deltas = []

        process_count = 0
        active_writers = 0

        # -------------------------------------------------
        # Collect raw process-level values
        # This mirrors your training-time raw monitor logic
        # -------------------------------------------------
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pid = proc.info["pid"]
                name = proc.info["name"] or "unknown"

                # CPU / MEM
                cpu = proc.cpu_percent(interval=None)
                mem = proc.memory_percent()

                # Disk write bytes
                try:
                    io = proc.io_counters()
                    write_bytes = io.write_bytes if io else 0
                except (psutil.AccessDenied, AttributeError):
                    write_bytes = 0

                key = (pid, name)

                # IMPORTANT FIX:
                # If process is first seen, initialize it and do NOT count fake delta
                if key not in previous_disk_writes:
                    previous_disk_writes[key] = write_bytes
                    delta = 0
                else:
                    prev = previous_disk_writes[key]
                    delta = max(0, write_bytes - prev)
                    previous_disk_writes[key] = write_bytes

                cpu_vals.append(cpu)
                mem_vals.append(mem)
                write_deltas.append(delta)

                process_count += 1
                if delta > 0:
                    active_writers += 1

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Safety
        if len(cpu_vals) == 0:
            print("[WARN] No process data collected this cycle.")
            time.sleep(INTERVAL)
            continue

        # -------------------------------------------------
        # Aggregate EXACTLY like your training extractor
        # -------------------------------------------------
        cpu_mean = float(np.mean(cpu_vals))
        cpu_max = float(np.max(cpu_vals))
        mem_mean = float(np.mean(mem_vals))

        disk_write_sum = float(np.sum(write_deltas))
        disk_write_max = float(np.max(write_deltas))
        disk_write_rate = float(disk_write_sum / max(active_writers, 1))

        features = np.array([[
            cpu_mean,
            cpu_max,
            mem_mean,
            disk_write_sum,
            disk_write_max,
            process_count,
            active_writers,
            disk_write_rate
        ]], dtype=np.float64)

        # -------------------------------------------------
        # Model inference
        # -------------------------------------------------
        prob = float(model.predict_proba(features)[0][1])
        instant_pred = 1 if prob >= PROB_THRESHOLD else 0

        if prob > max_prob:
            max_prob = prob
            max_prob_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        window_count += 1

        # Warm-up logic
        if window_count <= WARMUP_WINDOWS:
            rolling_preds.append(0)
            stable_pred = 0
            status = "WARMUP ⏳"
        else:
            rolling_preds.append(instant_pred)
            stable_pred = 1 if sum(rolling_preds) >= ALERT_MIN_HITS else 0
            status = "RANSOMWARE 🚨" if stable_pred == 1 else "BENIGN ✅"

        if instant_pred == 1:
            instant_ransom_hits += 1
        if stable_pred == 1:
            stable_ransom_hits += 1

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = {
            "timestamp": now,
            "cpu_mean": cpu_mean,
            "cpu_max": cpu_max,
            "mem_mean": mem_mean,
            "disk_write_sum": disk_write_sum,
            "disk_write_max": disk_write_max,
            "process_count": process_count,
            "active_writers": active_writers,
            "disk_write_rate": disk_write_rate,
            "ransomware_probability": prob,
            "instant_prediction": instant_pred,
            "stable_prediction": stable_pred,
            "rolling_hits": int(sum(rolling_preds))
        }

        history.append(row)

        # -------------------------------------------------
        # Print
        # -------------------------------------------------
        print("=" * 80)
        print(f"[{now}] {status}")
        print(f"  Instant Prob      : {prob:.3f}")
        print(f"  Rolling Hits      : {sum(rolling_preds)}/{ROLLING_WINDOW}")
        print(f"  Instant Pred      : {'RANSOMWARE' if instant_pred else 'BENIGN'}")
        print(f"  Stable Pred       : {'RANSOMWARE' if stable_pred else 'BENIGN'}")

        if PRINT_FEATURES:
            print(f"  cpu_mean          : {cpu_mean:.3f}")
            print(f"  cpu_max           : {cpu_max:.3f}")
            print(f"  mem_mean          : {mem_mean:.3f}")
            print(f"  disk_write_sum    : {disk_write_sum:.0f}")
            print(f"  disk_write_max    : {disk_write_max:.0f}")
            print(f"  process_count     : {process_count}")
            print(f"  active_writers    : {active_writers}")
            print(f"  disk_write_rate   : {disk_write_rate:.0f}")

        # Optional safety logging every loop
        if SAVE_ON_EVERY_LOOP and len(history) > 0:
            pd.DataFrame(history).to_csv(LOG_PATH, index=False)

        # Keep actual loop interval stable
        elapsed = time.time() - loop_start
        sleep_time = max(0, INTERVAL - elapsed)
        time.sleep(sleep_time)

# =========================================================
# INTERRUPT / SHUTDOWN
# =========================================================
except KeyboardInterrupt:
    end_time = datetime.now()
    duration = end_time - start_time

    df = pd.DataFrame(history)
    df.to_csv(LOG_PATH, index=False)

    print("\n" + "=" * 80)
    print("[INFO] LIVE DETECTOR INTERRUPTED BY USER")
    print("=" * 80)
    print(f"Start Time            : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End Time              : {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Run Duration          : {duration}")
    print(f"Total Windows         : {len(history)}")
    print(f"Instant Ransom Hits   : {instant_ransom_hits}")
    print(f"Stable Ransom Hits    : {stable_ransom_hits}")
    print(f"Max Probability Seen  : {max_prob:.3f}")
    print(f"Max Prob Timestamp    : {max_prob_timestamp}")
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

        if stable_ransom_hits > 0:
            print("\n[SUMMARY] Stable ransomware-like behavior WAS detected.")
        else:
            print("\n[SUMMARY] No stable ransomware detection occurred.")
    else:
        print("[WARN] No data was captured.")

    print("=" * 80)
