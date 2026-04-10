# fake_ransom_parallel.py

import os
import time
import multiprocessing

BASE_DIR = "data/ransomware/parallel"
os.makedirs(BASE_DIR, exist_ok=True)

def worker(worker_id):
    start = time.time()
    file_id = 0
    while time.time() - start < 35:
        fname = os.path.join(BASE_DIR, f"w{worker_id}_{file_id}.bin")
        with open(fname, "wb") as f:
            f.write(os.urandom(1024 * 60))  # 60 KB
        file_id += 1

if __name__ == "__main__":
    print("[INFO] Parallel Ransomware Started")

    processes = []
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("[INFO] Parallel Ransomware Finished")
