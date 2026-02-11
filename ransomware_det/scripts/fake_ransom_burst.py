import os
import time

BASE_DIR = "data/ransomware/burst"
os.makedirs(BASE_DIR, exist_ok=True)

print("[INFO] Fake ransomware (BURST) started")

file_id = 0

for cycle in range(10):
    # Burst phase
    for _ in range(50):
        fname = os.path.join(BASE_DIR, f"file_{file_id}.bin")
        with open(fname, "wb") as f:
            f.write(os.urandom(1024 * 40))  # 40 KB
        file_id += 1
        time.sleep(0.02)

    # Pause phase
    time.sleep(2)

print("[INFO] Fake ransomware (BURST) completed")
