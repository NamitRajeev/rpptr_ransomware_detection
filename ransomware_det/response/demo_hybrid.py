import pandas as pd
from hybrid_decision import hybrid_decision

# Load processed feature data
df = pd.read_csv("data/processed/labeled_features.csv")

# Separate benign and ransomware samples
benign_df = df[df["label"] == 0].reset_index(drop=True)
ransom_df = df[df["label"] == 1].reset_index(drop=True)

print("\n--- BENIGN SAMPLE DECISION ---")
benign_window = benign_df.tail(30)
decision, source = hybrid_decision(benign_window)
print("Decision:", decision)
print("Triggered by:", source)

print("\n--- RANSOMWARE SAMPLE DECISION ---")
ransom_window = ransom_df.tail(30)
decision, source = hybrid_decision(ransom_window)
print("Decision:", decision)
print("Triggered by:", source)
