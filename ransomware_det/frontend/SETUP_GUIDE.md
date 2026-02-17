# Setup Guide for R.A.P.T.O.R Dashboard

This guide will help you set up the backend and frontend to display real-time ransomware detection results.

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- Your detection files (`hybrid_decision.py`, `replay_realtime.py`)
- Your data files (CSV, model files)

## Step 1: Copy Your Detection Files

1. Navigate to the backend folder:
   ```bash
   cd d:\Coding\raptor\backend
   ```

2. Create a `response` folder:
   ```bash
   mkdir response
   ```

3. **Copy your detection files** to `backend/response/`:
   - Copy `hybrid_decision.py` from your response folder
   - The backend will automatically import this module

## Step 2: Copy Your Data Files

1. Create the data directory structure:
   ```bash
   mkdir -p data\processed
   ```

2. **Copy your CSV file** to `backend/data/processed/`:
   - Copy `labeled_features.csv` to this location

3. **If you have model files**, also copy them:
   - `rf_model.pkl` → `backend/model/rf_model.pkl`
   - `lstm_model.h5` → `backend/lstm/lstm_model.h5`
   - `scaler.pkl` → `backend/data/processed/scaler.pkl`
   - `benign_errors.npy` → `backend/data/processed/benign_errors.npy`

   Create directories as needed:
   ```bash
   mkdir model
   mkdir lstm
   ```

## Step 3: Install Backend Dependencies

```bash
cd d:\Coding\raptor\backend
pip install -r requirements.txt
```

This will install:
- FastAPI
- Uvicorn
- WebSockets
- Pandas, NumPy
- Scikit-learn, TensorFlow, Joblib

## Step 4: Install Frontend Dependencies

```bash
cd d:\Coding\raptor
npm install
```

## Step 5: Start the Backend Server

Open a terminal and run:

```bash
cd d:\Coding\raptor\backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## Step 6: Start the Frontend

Open a **new terminal** and run:

```bash
cd d:\Coding\raptor
npm run dev
```

You should see:
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

## Step 7: Open the Dashboard

1. Open your browser to: `http://localhost:5173`
2. You should see the R.A.P.T.O.R dashboard
3. Check the connection status at the top - it should say "● CONNECTED"
4. Click **"Start Detection"** to begin streaming

## Troubleshooting

### Backend Issues

**"Could not import hybrid_decision"**
- Make sure `hybrid_decision.py` is in `backend/response/` folder
- Check that all imports in `hybrid_decision.py` are available

**"Could not find labeled_features.csv"**
- Make sure the CSV is in `backend/data/processed/labeled_features.csv`
- The backend will use mock data if CSV is not found

**"Module not found" errors**
- Run `pip install -r requirements.txt` again
- Make sure you're in the backend directory

### Frontend Issues

**"CONNECTION ERROR" or "DISCONNECTED"**
- Make sure the backend is running on port 8000
- Check the backend terminal for errors
- Try refreshing the browser page

**No detections appearing**
- Click "Start Detection" button
- Check browser console (F12) for errors
- Check backend terminal for error messages

### Model Issues

If you get errors related to model files:
- The backend will fall back to mock detection if models aren't found
- Make sure all model file paths in `hybrid_decision.py` are correct
- You may need to adjust paths in `hybrid_decision.py` to be relative to the backend folder

## Expected Behavior

When everything is working:

1. **Connection Status**: Shows "● CONNECTED" in green
2. **Start Detection**: Clicking starts the stream
3. **Live Feed**: Detection logs appear in real-time
4. **Stats Update**: Cards show Total Detections, Normal Traffic, Total Attacks, Ransomware counts
5. **Color Coding**:
   - Green = BENIGN (normal behavior)
   - Red = RANSOMWARE (RF) (detected by Random Forest)
   - Orange = SUSPICIOUS (LSTM) (detected by LSTM anomaly)

## Next Steps

Once the dashboard is running:
- Let it run for 50-100 detections to see the accuracy
- Test the Pause and Reset buttons
- Monitor the backend terminal for accuracy output
- Verify the detection decisions match your expectations
