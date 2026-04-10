# Quick Start - R.A.P.T.O.R Dashboard

## Fastest Way to Get Started

### Option 1: Using Batch Scripts (Windows)

1. **Start Backend** (Terminal 1):
   ```bash
   cd d:\Coding\raptor\backend
   start_backend.bat
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd d:\Coding\raptor
   start_frontend.bat
   ```

3. **Open Dashboard**: Visit `http://localhost:5173`

### Option 2: Manual Commands

**Terminal 1 - Backend:**
```bash
cd d:\Coding\raptor\backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd d:\Coding\raptor
npm install
npm run dev
```

## Important: Copy Your Files First!

Before starting, you need to copy your detection files:

### 1. Copy Detection Module
```
backend/response/hybrid_decision.py  ← Copy your file here
```

### 2. Copy Data Files
```
backend/data/processed/labeled_features.csv  ← Copy your CSV here
```

### 3. (Optional) Copy Model Files
```
backend/model/rf_model.pkl
backend/lstm/lstm_model.h5
backend/data/processed/scaler.pkl
backend/data/processed/benign_errors.npy
```

**Note:** If you don't copy the files, the backend will use mock data for demonstration.

## What You Should See

✅ **Backend Terminal:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
[INFO] Successfully imported hybrid_decision module
[INFO] Loaded 1000 feature rows
```

✅ **Frontend Terminal:**
```
VITE v7.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

✅ **Dashboard:**
- Connection status: "● CONNECTED" (green)
- Click "Start Detection" to begin
- See real-time detection logs streaming

## Troubleshooting

**Backend won't start?**
- Make sure Python 3.8+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't start?**
- Make sure Node.js 16+ is installed: `node --version`
- Install dependencies: `npm install`

**Connection error?**
- Make sure backend is running on port 8000
- Check `.env` file has: `VITE_WS_URL=ws://localhost:8000/ws/detections`

For detailed setup instructions, see [SETUP_GUIDE.md](./SETUP_GUIDE.md)
