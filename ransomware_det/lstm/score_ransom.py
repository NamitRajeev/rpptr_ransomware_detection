import numpy as np
from tensorflow.keras.models import load_model

THRESHOLD = 0.018763839723465545
  # update after running anomaly_score.py

model = load_model("lstm/lstm_model.h5", compile=False)
X = np.load("data/processed/X_ransomware_sequences.npy")

X_pred = model.predict(X, verbose=0)
errors = np.mean((X - X_pred) ** 2, axis=(1, 2))

count = (errors > THRESHOLD).sum()

print(" Ransomware mean:", errors.mean())
print(" Above threshold:", count, "/", len(errors))
