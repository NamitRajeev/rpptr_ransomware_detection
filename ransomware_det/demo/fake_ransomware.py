import os
import time

TEST_DIR = "ransom_test_files"
TOTAL_FILES = 1000
SLEEP_PER_FILE = 0.04  # critical: allows interruption

if not os.path.exists(TEST_DIR):
    os.makedirs(TEST_DIR)

print("[INFO] Fake ransomware started")
print(f"[INFO] Intended damage: {TOTAL_FILES} files")

files_created = 0

try:
    for i in range(TOTAL_FILES):
        file_path = os.path.join(TEST_DIR, f"file_{i}.txt")

        with open(file_path, "w") as f:
            f.write("Simulated ransomware data\n" * 500)

        # dummy encryption
        with open(file_path, "rb") as f:
            data = f.read()

        encrypted = bytes([b ^ 123 for b in data])

        with open(file_path, "wb") as f:
            f.write(encrypted)

        files_created += 1

        if i % 50 == 0:
            print(f"[INFO] Files created so far: {files_created}")

        time.sleep(SLEEP_PER_FILE)

except KeyboardInterrupt:
    pass

finally:
    print("\n[SUMMARY]")
    print(f"Total files intended: {TOTAL_FILES}")
    print(f"Total files actually created: {files_created}")
    print("[INFO] Fake ransomware terminated")
