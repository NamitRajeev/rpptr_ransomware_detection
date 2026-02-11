import os
import time
import random

BASE_DIR = "data/ransomware/slow"
os.makedirs(BASE_DIR, exist_ok=True)

print("[INFO] Fake ransomware (SLOW) started")

for i in range(300):
    fname = os.path.join(BASE_DIR, f"file_{i}.bin")

    with open(fname, "wb") as f:
        f.write(os.urandom(1024 * 20))  # 20 KB

    # Long delay (stealth)
    time.sleep(random.uniform(0.5, 1.2))

print("[INFO] Fake ransomware (SLOW) completed")
