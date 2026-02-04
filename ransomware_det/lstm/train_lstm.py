import os
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, RepeatVector, TimeDistributed
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# ================= PATH SETUP =================

# Project root: ransomware_det/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEQS_DIR = os.path.join(BASE_DIR, "lstm", "seqs")

X_PATH = os.path.join(SEQS_DIR, "X_sequences.npy")
Y_PATH = os.path.join(SEQS_DIR, "y_sequences.npy")

MODEL_PATH = os.path.join(BASE_DIR, "lstm", "lstm_model.h5")

# ================= LOAD DATA =================

print("[INFO] Loading sequence data...")

if not os.path.exists(X_PATH) or not os.path.exists(Y_PATH):
    raise FileNotFoundError("Sequence files not found in lstm/seqs/")

X = np.load(X_PATH)
y = np.load(Y_PATH)

print("[INFO] X shape:", X.shape)
print("[INFO] y shape:", y.shape)

# ================= SELECT BENIGN DATA =================
# 0 = benign, 1 = ransomware-like

X_benign = X[y == 0]

print("[INFO] Benign sequences:", X_benign.shape[0])

if X_benign.shape[0] < 10:
    raise ValueError("Not enough benign sequences to train LSTM")

# ================= MODEL CONFIG =================

timesteps = X_benign.shape[1]
features = X_benign.shape[2]

input_layer = Input(shape=(timesteps, features))

# -------- Encoder --------
encoded = LSTM(64, activation="tanh", return_sequences=True)(input_layer)
encoded = LSTM(32, activation="tanh", return_sequences=False)(encoded)

# -------- Bottleneck --------
bottleneck = RepeatVector(timesteps)(encoded)

# -------- Decoder --------
decoded = LSTM(32, activation="tanh", return_sequences=True)(bottleneck)
decoded = LSTM(64, activation="tanh", return_sequences=True)(decoded)

output_layer = TimeDistributed(Dense(features))(decoded)

# -------- Autoencoder --------
autoencoder = Model(inputs=input_layer, outputs=output_layer)

autoencoder.compile(
    optimizer=Adam(learning_rate=0.001),
    loss="mse"
)

autoencoder.summary()

# ================= TRAIN =================

early_stop = EarlyStopping(
    monitor="loss",
    patience=5,
    restore_best_weights=True
)

print("[INFO] Training LSTM autoencoder...")

autoencoder.fit(
    X_benign,
    X_benign,
    epochs=50,
    batch_size=8,
    shuffle=True,
    callbacks=[early_stop]
)

# ================= SAVE MODEL =================

autoencoder.save(MODEL_PATH)

print("\n========== SUCCESS ==========")
print("[INFO] LSTM autoencoder trained successfully")
print("[INFO] Model saved at:", MODEL_PATH)
print("=============================")
