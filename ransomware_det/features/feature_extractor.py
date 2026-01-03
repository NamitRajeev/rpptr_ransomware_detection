import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_CSV = os.path.join(DATA_DIR, "process_activity_log.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "features.csv")

print("[INFO] Loading:", INPUT_CSV)

df = pd.read_csv(INPUT_CSV)
df["timestamp"] = pd.to_datetime(df["timestamp"])

grouped = df.groupby(["pid", "process_name"])
rows = []

for (pid, name), g in grouped:
    rows.append([
        pid,
        name,
        g["cpu_percent"].mean(),
        g["cpu_percent"].max(),
        g["memory_percent"].mean(),
        g["disk_write_delta"].sum(),
        g["disk_write_delta"].max(),
        (g["timestamp"].max() - g["timestamp"].min()).total_seconds()
    ])

features = pd.DataFrame(rows, columns=[
    "pid",
    "process_name",
    "avg_cpu",
    "max_cpu",
    "avg_memory",
    "total_disk_write",
    "max_write_burst",
    "process_lifetime"
])

features.to_csv(OUTPUT_CSV, index=False)

print("[INFO] Features saved to:", OUTPUT_CSV)
