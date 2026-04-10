# R.A.P.T.O.R Backend

FastAPI backend for real-time ransomware detection streaming.

## Setup Instructions

### 1. Copy Your Detection Files

Create a `response` folder in the backend directory and copy your detection files:

```bash
cd backend
mkdir response
```

Copy these files to `backend/response/`:
- `hybrid_decision.py`
- Any other dependencies from your response folder

### 2. Copy Your Data Files

Create the data directory structure and copy your dataset:

```bash
mkdir -p data/processed
```

Copy these files to `backend/data/processed/`:
- `labeled_features.csv`

If you have the model files, also copy:
- `model/rf_model.pkl` → `backend/model/rf_model.pkl`
- `lstm/lstm_model.h5` → `backend/lstm/lstm_model.h5`
- `data/processed/scaler.pkl` → `backend/data/processed/scaler.pkl`
- `data/processed/benign_errors.npy` → `backend/data/processed/benign_errors.npy`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `WebSocket /ws/detections` - Real-time detection stream

## WebSocket Commands

Send JSON commands to control the detection stream:

```json
{"command": "start"}   // Start detection streaming
{"command": "stop"}    // Pause detection streaming
{"command": "reset"}   // Reset detection state
```

## Directory Structure

```
backend/
├── main.py                    # FastAPI application
├── detection_service.py       # Detection streaming service
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── response/                  # Your detection modules (copy here)
│   └── hybrid_decision.py
├── data/
│   └── processed/
│       ├── labeled_features.csv
│       ├── scaler.pkl
│       └── benign_errors.npy
├── model/
│   └── rf_model.pkl
└── lstm/
    └── lstm_model.h5
```

## Testing

1. Start the backend server
2. Visit `http://localhost:8000` to see API info
3. Check `http://localhost:8000/health` for health status
4. Connect the frontend to test WebSocket streaming
