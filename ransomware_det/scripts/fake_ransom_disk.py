# fake_ransom_disk_flood.py

import os
import time

BASE_DIR = "data/ransomware/disk_flood"
os.makedirs(BASE_DIR, exist_ok=True)

print("[INFO] Disk Flood Ransomware Started")

start = time.time()
file_id = 0

while time.time() - start < 40:
    fname = os.path.join(BASE_DIR, f"file_{file_id}.bin")
    with open(fname, "wb") as f:
        f.write(os.urandom(1024 * 200))  # 200 KB large write
    file_id += 1

print("[INFO] Disk Flood Finished")
