import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# -------------------------------
# Resolve paths safely
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "labeled_features.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "rf_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

print("[INFO] Loading dataset from:", DATA_PATH)

# Load dataset
df = pd.read_csv(DATA_PATH)

# -------------------------------
# Separate features and labels
# -------------------------------
X = df.drop(columns=["label", "pid", "process_name"])
y = df["label"]

print("[INFO] Feature columns:", list(X.columns))

# -------------------------------
# Train-test split
# -------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

print("[INFO] Training samples:", len(X_train))
print("[INFO] Testing samples:", len(X_test))

# -------------------------------
# Train Random Forest
# -------------------------------
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=None,
    random_state=42,
    class_weight="balanced"
)

rf.fit(X_train, y_train)

print("[INFO] Model training completed")

# -------------------------------
# Evaluation
# -------------------------------
y_pred = rf.predict(X_test)

print("\n[RESULT] Accuracy:", accuracy_score(y_test, y_pred))
print("\n[RESULT] Classification Report:\n", classification_report(y_test, y_pred))
print("\n[RESULT] Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# -------------------------------
# Save model
# -------------------------------
joblib.dump(rf, MODEL_PATH)
print("\n[INFO] Model saved to:", MODEL_PATH)
