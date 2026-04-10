import os
import shutil
import time

# -------- CONFIG --------
SRC_DIR = r"C:\Windows\System32"          # Source of legitimate files
DST_DIR = r"data\benign\copy"             # Destination directory
MAX_FILES = 300                           # Number of files to copy
SLEEP_BETWEEN_COPIES = 0.01               # Small delay for realism
# ------------------------

os.makedirs(DST_DIR, exist_ok=True)

print("[WORKLOAD] benign_copy_start")

copied = 0

for root, dirs, files in os.walk(SRC_DIR):
    for file in files:
        if copied >= MAX_FILES:
            break

        src_path = os.path.join(root, file)
        dst_path = os.path.join(DST_DIR, f"{copied}_{file}")

        try:
            shutil.copy2(src_path, dst_path)
            copied += 1
            time.sleep(SLEEP_BETWEEN_COPIES)
        except (PermissionError, FileNotFoundError, OSError):
            # Expected on Windows system directories
            continue

print(f"[INFO] Copied {copied} files successfully")
print("[WORKLOAD] benign_copy_end")
