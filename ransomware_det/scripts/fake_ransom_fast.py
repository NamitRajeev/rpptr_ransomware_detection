import os
import time
import random

BASE_DIR = "data/ransomware/fast"
os.makedirs(BASE_DIR, exist_ok=True)

print("[INFO] Fake ransomware (FAST) started")

for i in range(1000):
    fname = os.path.join(BASE_DIR, f"file_{i}.bin")

    # Large random write (simulates encryption output)
    with open(fname, "wb") as f:
        f.write(os.urandom(1024 * 50))  # 50 KB

    # Very small delay
    time.sleep(0.01)

print("[INFO] Fake ransomware (FAST) completed")
