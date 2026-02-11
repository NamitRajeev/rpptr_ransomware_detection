import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, RepeatVector, TimeDistributed, Dense
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

X = np.load("data/processed/X_sequences.npy")

SEQ_LEN = X.shape[1]
N_FEATURES = X.shape[2]  # 🔴 now 8

inputs = Input(shape=(SEQ_LEN, N_FEATURES))

x = LSTM(64, return_sequences=True)(inputs)
x = LSTM(32)(x)
x = RepeatVector(SEQ_LEN)(x)
x = LSTM(32, return_sequences=True)(x)
x = LSTM(64, return_sequences=True)(x)

outputs = TimeDistributed(Dense(N_FEATURES))(x)

model = Model(inputs, outputs)
model.compile(optimizer="adam", loss="mse")

model.fit(
    X, X,
    epochs=50,
    batch_size=32,
    callbacks=[
        EarlyStopping(patience=5, restore_best_weights=True),
        ModelCheckpoint("lstm/lstm_model.h5", save_best_only=True)
    ]
)

print("[INFO] LSTM training completed")
