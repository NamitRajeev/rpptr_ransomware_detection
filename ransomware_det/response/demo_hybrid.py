import pandas as pd
from hybrid_decision import hybrid_decision

df = pd.read_csv("data/processed/labeled_features.csv")

benign_df = df[df["label"] == 0].reset_index(drop=True)
ransom_df = df[df["label"] == 1].reset_index(drop=True)

print("\n==============================")
print("      HYBRID MODEL DEMO")
print("==============================")

# BENIGN TEST
print("\n--- BENIGN SAMPLE ---")
benign_window = benign_df.tail(30)
result = hybrid_decision(benign_window)

print("RF Probability:", round(result["rf_prob"], 3))
print("LSTM Score:", round(result["lstm_score"], 6))
print("Threshold:", round(result["threshold"], 6))
print("Final Decision:", result["decision"])

# RANSOMWARE TEST
print("\n--- RANSOMWARE SAMPLE ---")
ransom_window = ransom_df.tail(30)
result = hybrid_decision(ransom_window)

print("RF Probability:", round(result["rf_prob"], 3))
print("LSTM Score:", round(result["lstm_score"], 6))
print("Threshold:", round(result["threshold"], 6))
print("Final Decision:", result["decision"])
