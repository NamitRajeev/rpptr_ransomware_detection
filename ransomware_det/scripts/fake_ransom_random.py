# fake_ransom_irregular.py

import os
import time
import random

BASE_DIR = "data/ransomware/irregular"
os.makedirs(BASE_DIR, exist_ok=True)

print("[INFO] Irregular Ransomware Started")

file_id = 0

for _ in range(15):
    # Burst
    for _ in range(random.randint(20, 80)):
        fname = os.path.join(BASE_DIR, f"file_{file_id}.bin")
        with open(fname, "wb") as f:
            f.write(os.urandom(1024 * random.randint(20, 80)))
        file_id += 1

    # Random idle
    time.sleep(random.uniform(0.5, 2))

print("[INFO] Irregular Ransomware Finished")
