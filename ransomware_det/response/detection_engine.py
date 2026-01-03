import psutil
import time
import joblib
import pandas as pd
import os
from datetime import datetime

# ------------------ LOAD MODEL ------------------

MODEL_PATH = os.path.join("model", "rf_model.pkl")
rf_model = joblib.load(MODEL_PATH)

print("[INFO] Random Forest model loaded successfully")

# ------------------ CONFIG ------------------

FEATURE_COLUMNS = [
    "avg_cpu",
    "max_cpu",
    "avg_memory",
    "total_disk_write",
    "max_write_burst",
    "process_lifetime"
]

# Balanced, viva-safe parameters
MIN_SAMPLES = 2
CONFIRMATION_COUNT = 2
CONFIDENCE_THRESHOLD = 0.4

# Demo scope: only monitor python ransomware
TARGET_PROCESSES = ["python.exe"]

# ------------------ STATE ------------------

process_history = {}
suspicious_count = {}

print("[INFO] Real-time ransomware detection started")

# ------------------ MAIN LOOP ------------------

while True:
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']

            if not name:
                continue

            name_lower = name.lower()

            # Restrict scope for safety & demo clarity
            if name_lower not in TARGET_PROCESSES:
                continue

            cpu = proc.cpu_percent(interval=0.1)
            memory = proc.memory_percent()

            io = proc.io_counters()
            write_bytes = io.write_bytes if io else 0

            now = datetime.now()

            # Initialize tracking
            if pid not in process_history:
                process_history[pid] = {
                    "start_time": now,
                    "cpu": [],
                    "memory": [],
                    "writes": []
                }
                suspicious_count[pid] = 0

            hist = process_history[pid]
            hist["cpu"].append(cpu)
            hist["memory"].append(memory)
            hist["writes"].append(write_bytes)

            # Wait for minimum behavioral evidence
            if len(hist["cpu"]) < MIN_SAMPLES:
                continue

            # ------------------ FEATURE EXTRACTION ------------------

            features = {
                "avg_cpu": sum(hist["cpu"]) / len(hist["cpu"]),
                "max_cpu": max(hist["cpu"]),
                "avg_memory": sum(hist["memory"]) / len(hist["memory"]),
                "total_disk_write": sum(hist["writes"]),
                "max_write_burst": max(hist["writes"]),
                "process_lifetime": (now - hist["start_time"]).total_seconds()
            }

            X = pd.DataFrame([features])[FEATURE_COLUMNS]

            prediction = rf_model.predict(X)[0]
            confidence = max(rf_model.predict_proba(X)[0])

            # ------------------ DECISION LOGIC ------------------

            if prediction == 1 and confidence >= CONFIDENCE_THRESHOLD:
                suspicious_count[pid] += 1
            else:
                suspicious_count[pid] = 0

            # ------------------ RESPONSE ------------------

            if suspicious_count[pid] >= CONFIRMATION_COUNT:
                print("\n[ALERT] Ransomware detected!")
                print(f"        PID: {pid}")
                print(f"        Process: {name}")
                print(f"        Confidence: {confidence:.2f}")

                try:
                    psutil.Process(pid).terminate()
                    print(f"[ACTION] Process {pid} terminated")
                except Exception as e:
                    print(f"[ERROR] Failed to terminate {pid}: {e}")

                print("[INFO] Ransomware neutralized. Stopping detection engine.")
                exit(0)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(1)

