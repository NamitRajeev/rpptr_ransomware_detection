import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_CSV = os.path.join(DATA_DIR, "features.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "labeled_features.csv")

print("[INFO] Loading features from:", INPUT_CSV)

df = pd.read_csv(INPUT_CSV)

# Simple heuristic labeling (demo purpose)
df["label"] = (df["total_disk_write"] > df["total_disk_write"].median()).astype(int)

df.to_csv(OUTPUT_CSV, index=False)

print("[INFO] Labeling completed")
print("[INFO] Label distribution:")
print(df["label"].value_counts())
