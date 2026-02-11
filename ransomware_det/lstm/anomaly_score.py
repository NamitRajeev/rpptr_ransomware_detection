import numpy as np
from tensorflow.keras.models import load_model

model = load_model("lstm/lstm_model.h5", compile=False)
X = np.load("data/processed/X_sequences.npy")

X_pred = model.predict(X, verbose=0)

errors = np.mean((X - X_pred) ** 2, axis=(1, 2))

mean = errors.mean()
std = errors.std()
threshold = mean + 3 * std

print("Mean:", mean)
print("Std:", std)
print("Threshold:", threshold)

np.save("data/processed/benign_recon_errors.npy", errors)
