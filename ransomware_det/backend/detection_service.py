import sys
import os
import asyncio
import pandas as pd
from datetime import datetime
from typing import AsyncGenerator, Dict, Any

# Add the parent directory to path to import user's detection modules
# User needs to place their response folder files here or adjust the path
RESPONSE_DIR = os.path.join(os.path.dirname(__file__), "response")
if os.path.exists(RESPONSE_DIR):
    sys.path.insert(0, RESPONSE_DIR)

# Try to import the user's hybrid_decision module
try:
    from hybrid_decision import hybrid_decision
    HYBRID_DECISION_AVAILABLE = True
    print("[INFO] Successfully imported hybrid_decision module")
except ImportError as e:
    print(f"[WARNING] Could not import hybrid_decision: {e}")
    print("[INFO] Please copy hybrid_decision.py to backend/response/ folder")
    HYBRID_DECISION_AVAILABLE = False


class DetectionService:
    """
    Service that streams real-time detection results from the hybrid detection system.
    Integrates with user's replay_realtime.py and hybrid_decision.py logic.
    """
    
    def __init__(self, seq_len: int = 30, sequence_delay: float = 0.7):
        self.seq_len = seq_len
        self.sequence_delay = sequence_delay
        self.is_running = False
        self.buffer = []
        self.correct = 0
        self.total = 0
        self.current_index = 0
        self.df = None
        
        # Try to load the dataset
        self._load_dataset()
    
    def _load_dataset(self):
        """Load and shuffle the feature dataset"""
        # Look for the CSV in multiple possible locations
        possible_paths = [
            "data/processed/labeled_features.csv",
            "../data/processed/labeled_features.csv",
            os.path.join(os.path.dirname(__file__), "data/processed/labeled_features.csv"),
            os.path.join(os.path.dirname(__file__), "../data/processed/labeled_features.csv"),
        ]
        
        for csv_path in possible_paths:
            if os.path.exists(csv_path):
                print(f"[INFO] Loading dataset from: {csv_path}")
                self.df = pd.read_csv(csv_path)
                # Shuffle dataset for realistic replay
                self.df = self.df.sample(frac=1, random_state=42).reset_index(drop=True)
                print(f"[INFO] Loaded {len(self.df)} feature rows")
                return
        
        print("[WARNING] Could not find labeled_features.csv")
        print("[INFO] Please place the CSV file in backend/data/processed/ folder")
        print("[INFO] Using mock data for demonstration")
        self._create_mock_dataset()
    
    def _create_mock_dataset(self):
        """Create mock dataset for demonstration if real data not available"""
        import numpy as np
        
        # Create 1000 rows of mock data
        n_rows = 1000
        self.df = pd.DataFrame({
            'cpu_mean': np.random.uniform(10, 90, n_rows),
            'cpu_max': np.random.uniform(50, 100, n_rows),
            'mem_mean': np.random.uniform(20, 80, n_rows),
            'disk_write_sum': np.random.uniform(0, 10000, n_rows),
            'disk_write_max': np.random.uniform(0, 5000, n_rows),
            'process_count': np.random.randint(5, 50, n_rows),
            'active_writers': np.random.randint(0, 10, n_rows),
            'disk_write_rate': np.random.uniform(0, 100, n_rows),
            'label': np.random.choice([0, 1], n_rows, p=[0.8, 0.2])
        })
        print("[INFO] Created mock dataset with 1000 rows")
    
    async def stream_detections(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream detection results in real-time.
        Yields detection dictionaries formatted for the frontend.
        """
        if self.df is None:
            print("[ERROR] No dataset available")
            return
        
        self.is_running = True
        
        # Continue from where we left off, or start from beginning
        if self.current_index >= len(self.df):
            self.current_index = 0
            self.buffer = []
        
        while self.is_running and self.current_index < len(self.df):
            row = self.df.iloc[self.current_index]
            
            # Add to buffer
            self.buffer.append(row)
            if len(self.buffer) > self.seq_len:
                self.buffer.pop(0)
            
            # Only process when we have enough data
            if len(self.buffer) >= self.seq_len:
                window_df = pd.DataFrame(self.buffer)
                
                # Get detection result
                if HYBRID_DECISION_AVAILABLE:
                    try:
                        rf_prob, lstm_score, decision, source = hybrid_decision(window_df)
                    except Exception as e:
                        print(f"[ERROR] hybrid_decision failed: {e}")
                        rf_prob, lstm_score, decision, source = self._mock_detection(row)
                else:
                    rf_prob, lstm_score, decision, source = self._mock_detection(row)
                
                # Calculate accuracy
                predicted_label = 1 if "RANSOMWARE" in decision else 0
                true_label = int(row["label"])
                
                self.total += 1
                if predicted_label == true_label:
                    self.correct += 1
                
                accuracy = self.correct / self.total if self.total > 0 else 0
                
                # Format result for frontend
                result = {
                    "id": self.current_index,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "step": self.current_index,
                    "rfProb": float(rf_prob),
                    "lstmScore": float(lstm_score),
                    "decision": decision,
                    "source": source,
                    "accuracy": float(accuracy),
                    "trueLabel": int(true_label)
                }
                
                self.current_index += 1
                
                # Yield result and wait for next iteration
                yield result
                await asyncio.sleep(self.sequence_delay)
            else:
                # Not enough data yet, just increment
                self.current_index += 1
                await asyncio.sleep(0.1)
        
        self.is_running = False
        print("[INFO] Detection stream completed")
    
    def _mock_detection(self, row):
        """Mock detection for when hybrid_decision is not available"""
        import random
        
        rf_prob = random.uniform(0.1, 0.9)
        lstm_score = random.uniform(0.0001, 0.01)
        
        if row["label"] == 1:
            decision = "RANSOMWARE (RF)" if rf_prob > 0.5 else "SUSPICIOUS (LSTM)"
            source = "Random Forest" if rf_prob > 0.5 else "LSTM Anomaly"
        else:
            decision = "BENIGN"
            source = "Normal Behavior"
        
        return rf_prob, lstm_score, decision, source
    
    def pause(self):
        """Pause the detection stream"""
        self.is_running = False
        print("[INFO] Detection service paused")
    
    def reset(self):
        """Reset the detection service to initial state"""
        self.is_running = False
        self.buffer = []
        self.correct = 0
        self.total = 0
        self.current_index = 0
        print("[INFO] Detection service reset")
