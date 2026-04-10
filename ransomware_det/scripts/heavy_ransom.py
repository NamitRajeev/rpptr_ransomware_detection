import os
import time
import random

TARGET_DIR = r"C:\Users\rpptr\OneDrive\Desktop\ransomware_det\data"
os.makedirs(TARGET_DIR, exist_ok=True)

print("[INFO] Starting training-compatible ransomware simulation...")

for cycle in range(10):
    print(f"[INFO] Cycle {cycle + 1}/10")

    for i in range(80):
        filename = os.path.join(
            TARGET_DIR,
            f"enc_{cycle}_{i}_{random.randint(1000,9999)}.bin"
        )

        # 512 KB to 1 MB writes
        size = random.randint(512 * 1024, 1024 * 1024)

        with open(filename, "wb") as f:
            f.write(os.urandom(size))
            f.flush()
            os.fsync(f.fileno())

    # short pause between bursts
    time.sleep(2)

print("[INFO] Simulation complete.")
