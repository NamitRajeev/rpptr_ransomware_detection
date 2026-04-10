import hashlib
import time

print("[INFO] Benign CPU-heavy workload started")

data = b"normal_computation"

for _ in range(300):
    for _ in range(3000):
        data = hashlib.sha256(data).digest()
    time.sleep(0.02)

print("[INFO] Benign CPU-heavy workload completed")
