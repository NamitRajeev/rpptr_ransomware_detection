import os
import pandas as pd
import numpy as np

# ================= PATH SETUP =================

# Project root: ransomware_det/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input: baseline RF dataset
INPUT_CSV = os.path.join(BASE_DIR, "data", "labeled_features.csv")

# Output: LSTM-specific data
SEQS_DIR = os.path.join(BASE_DIR, "lstm", "seqs")
os.makedirs(SEQS_DIR, exist_ok=True)

X_OUTPUT_PATH = os.path.join(SEQS_DIR, "X_sequences.npy")
Y_OUTPUT_PATH = os.path.join(SEQS_DIR, "y_sequences.npy")

# ================= CONFIG =================

SEQUENCE_LENGTH = 10  # timesteps per sequence

FEATURE_COLUMNS = [
    "avg_cpu",
    "max_cpu",
    "avg_memory",
    "total_disk_write",
    "max_write_burst",
    "process_lifetime"
]

LABEL_COLUMN = "label"
PROCESS_COLUMN = "process_name"

# ================= LOAD DATA =================

print("[INFO] Loading labeled dataset...")
if not os.path.exists(INPUT_CSV):
    raise FileNotFoundError(f"Input file not found: {INPUT_CSV}")

df = pd.read_csv(INPUT_CSV)
print(f"[INFO] Rows loaded: {len(df)}")

# ================= VALIDATION =================

required_cols = FEATURE_COLUMNS + [LABEL_COLUMN, PROCESS_COLUMN]
missing_cols = [c for c in required_cols if c not in df.columns]

if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")

# ================= NORMALIZATION =================
# (important for stable LSTM training)

print("[INFO] Normalizing features...")
df[FEATURE_COLUMNS] = (
    df[FEATURE_COLUMNS] - df[FEATURE_COLUMNS].mean()
) / df[FEATURE_COLUMNS].std()

# ================= SEQUENCE GENERATION =================

print("[INFO] Creating time-series sequences...")
grouped = df.groupby(PROCESS_COLUMN)

X_sequences = []
y_sequences = []

for process_name, group in grouped:
    group = group.sort_index()  # preserve temporal order

    features = group[FEATURE_COLUMNS].values
    labels = group[LABEL_COLUMN].values

    if len(features) < SEQUENCE_LENGTH:
        continue

    for i in range(len(features) - SEQUENCE_LENGTH + 1):
        X_sequences.append(features[i:i + SEQUENCE_LENGTH])
        y_sequences.append(labels[i + SEQUENCE_LENGTH - 1])

X_sequences = np.array(X_sequences)
y_sequences = np.array(y_sequences)

# ================= SAVE OUTPUT =================

np.save(X_OUTPUT_PATH, X_sequences)
np.save(Y_OUTPUT_PATH, y_sequences)

# ================= FINAL OUTPUT =================

print("\n========== SUCCESS ==========")
print("X shape:", X_sequences.shape)
print("y shape:", y_sequences.shape)
print("Saved to:", SEQS_DIR)
print("=============================")
