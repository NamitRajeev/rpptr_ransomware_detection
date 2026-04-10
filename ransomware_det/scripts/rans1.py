import os
import time

BASE_DIR = "data/ransomware/demo"
os.makedirs(BASE_DIR, exist_ok=True)

print("[INFO] Demo ransomware started")

end_time = time.time() + 40  # 40 seconds sustained activity

i = 0
while time.time() < end_time:
    fname = os.path.join(BASE_DIR, f"file_{i}.bin")
    with open(fname, "wb") as f:
        f.write(os.urandom(1024 * 200))  # 200KB

    i += 1
    time.sleep(0.05)

print("[INFO] Demo ransomware completed")
