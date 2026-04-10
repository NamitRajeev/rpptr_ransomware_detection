import pandas as pd
import os

BENIGN_DIR = "data/benign"
RANSOMWARE_DIR = "data/ransomware"
OUTPUT_DIR = "data/processed"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_folder(folder_path, label):
    all_dfs = []

    for file in os.listdir(folder_path):
        if not file.endswith(".csv"):
            continue

        path = os.path.join(folder_path, file)
        df = pd.read_csv(path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        agg = df.groupby("timestamp").agg(
            cpu_mean=("cpu_percent", "mean"),
            cpu_max=("cpu_percent", "max"),
            mem_mean=("memory_percent", "mean"),
            disk_write_sum=("disk_write_delta", "sum"),
            disk_write_max=("disk_write_delta", "max"),
            process_count=("pid", "count"),
            active_writers=("disk_write_delta", lambda x: (x > 0).sum())
        ).reset_index()

        # 🔴 NEW FEATURE (CRITICAL FIX)
        agg["disk_write_rate"] = agg["disk_write_sum"] / agg["active_writers"].clip(lower=1)

        agg["label"] = label
        all_dfs.append(agg)

    return pd.concat(all_dfs, ignore_index=True) if all_dfs else None


print("[INFO] Processing benign data...")
benign_df = process_folder(BENIGN_DIR, label=0)

print("[INFO] Processing ransomware data...")
ransomware_df = process_folder(RANSOMWARE_DIR, label=1)

full_df = pd.concat([benign_df, ransomware_df], ignore_index=True)

full_df.drop(columns=["label"]).to_csv(
    os.path.join(OUTPUT_DIR, "features.csv"), index=False
)

full_df.to_csv(
    os.path.join(OUTPUT_DIR, "labeled_features.csv"), index=False
)

print("[INFO] Feature aggregation completed")
