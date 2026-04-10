# features/process_monitor_live.py

import psutil
import time
import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(DATA_DIR, "live_process_log.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# Overwrite file fresh for each run
with open(LOG_PATH, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "timestamp",
        "pid",
        "process_name",
        "cpu_percent",
        "memory_percent",
        "disk_write_delta"
    ])

print("[INFO] LIVE monitoring started...")

previous_disk_writes = {}

try:
    while True:
        with open(LOG_PATH, "a", newline="") as f:
            writer = csv.writer(f)

            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    pid = proc.info["pid"]
                    name = proc.info["name"] or "unknown"

                    cpu = proc.cpu_percent(interval=0.0)
                    mem = proc.memory_percent()

                    io = proc.io_counters()
                    write_bytes = io.write_bytes if io else 0

                    prev = previous_disk_writes.get(pid, write_bytes)
                    delta = write_bytes - prev
                    previous_disk_writes[pid] = write_bytes

                    writer.writerow([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        pid,
                        name,
                        round(cpu, 3),
                        round(mem, 3),
                        delta
                    ])

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n[INFO] Live monitoring stopped.")
