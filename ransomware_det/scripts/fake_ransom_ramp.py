# fake_ransom_ramp.py

import os
import time

BASE_DIR = "data/ransomware/ramp"
os.makedirs(BASE_DIR, exist_ok=True)

print("[INFO] Ramp Ransomware Started")

file_id = 0

for delay in [0.5, 0.3, 0.15, 0.05, 0.01]:
    start = time.time()
    while time.time() - start < 8:
        fname = os.path.join(BASE_DIR, f"file_{file_id}.bin")
        with open(fname, "wb") as f:
            f.write(os.urandom(1024 * 40))
        file_id += 1
        time.sleep(delay)

print("[INFO] Ramp Ransomware Finished")
