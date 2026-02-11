import os
import zipfile
import time

BASE_DIR = r"data\benign\compress"
os.makedirs(BASE_DIR, exist_ok=True)

print("[WORKLOAD] benign_compress_start")

zip_path = os.path.join(BASE_DIR, "test_compress.zip")

# Create many small files and add to zip
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for i in range(400):
        fname = os.path.join(BASE_DIR, f"file_{i}.txt")

        # Create temporary file
        with open(fname, "w") as f:
            f.write("A" * 5000)

        # Add to zip
        z.write(fname)

        # Remove the temporary file
        os.remove(fname)

        time.sleep(0.005)

print("[INFO] Compression workload completed")
print("[WORKLOAD] benign_compress_end")
