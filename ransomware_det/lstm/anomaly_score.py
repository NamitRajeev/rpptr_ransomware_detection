# lstm/anomaly_score.py

import numpy as np

# -------------------------------------------------
# Deployment-calibrated anomaly threshold
# -------------------------------------------------
MEAN_ERROR = 0.3861410603439466
STD_ERROR = 0.004515529867134235
ANOMALY_THRESHOLD = 0.409  # slightly relaxed (mean + ~5*std)


def anomaly_score(model, sequence):
    """
    Compute reconstruction error for a single sequence.
    sequence shape must be (30, 8)
    """

    if sequence.ndim != 2:
        raise ValueError(f"Expected (30, 8), got {sequence.shape}")

    sequence = np.expand_dims(sequence, axis=0)

    reconstructed = model.predict(sequence, verbose=0)

    error = np.mean((sequence - reconstructed) ** 2)

    return float(error)


def is_anomalous(error):
    return error > ANOMALY_THRESHOLD
