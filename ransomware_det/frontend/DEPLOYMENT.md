# R.A.P.T.O.R Deployment Guide

## Overview

This guide will help you deploy the R.A.P.T.O.R detection dashboard on your system with the FastAPI detection engine.

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Your RF + LSTM hybrid detection models

## Directory Structure

```
raptor/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── detection_interface.py     # Detection engine interface (customize this)
│   ├── requirements.txt           # Python dependencies
│   └── __init__.py
├── src/
│   └── Dashboard.tsx              # React dashboard (WebSocket client)
├── .env                           # Environment variables
└── dist/                          # Built React app (after npm run build)
```

## Step 1: Set Up the Backend

### 1.1 Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Integrate Your Detection Engine

Edit `backend/detection_interface.py`:

1. **Import your models** in the `__init__` method:
   ```python
   def __init__(self):
       self.rf_model = load_model('path/to/your/rf_model.pkl')
       self.lstm_model = load_model('path/to/your/lstm_model.h5')
       self.scaler = load_scaler('path/to/your/scaler.pkl')
   ```

2. **Replace `simulate_detection()`** with your actual detection logic in `get_next_detection()`:
   ```python
   def get_next_detection(self, step: int):
       # Get your sliding window data
       window_data = self.get_window_data()
       
       # Preprocess
       processed = self.preprocess(window_data)
       
       # Get predictions
       rf_prob = self.rf_model.predict_proba(processed)[0][1]
       lstm_score = self.lstm_model.predict(processed)[0][0]
       
       # Apply hybrid decision
       decision, source = self.hybrid_decision(rf_prob, lstm_score)
       
       return {
           "rf_probability": rf_prob,
           "lstm_score": lstm_score,
           "decision": decision,
           "source": source
       }
   ```

3. **Implement your hybrid decision logic** in the `hybrid_decision()` method

### 1.3 Test the Backend

```bash
# From the backend directory
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000/api/health` to verify the server is running.

## Step 2: Build the Frontend

### 2.1 Install Dependencies

```bash
# From the project root
npm install
```

### 2.2 Configure Environment

Edit `.env` if your FastAPI server is not on `localhost:8000`:

```env
VITE_WS_URL=ws://YOUR_SERVER_IP:8000/ws/detections
```

### 2.3 Build for Production

```bash
npm run build
```

This creates a `dist/` folder with the optimized React app.

## Step 3: Deploy Together

### Option A: Serve React from FastAPI (Recommended)

1. **Uncomment the static file serving code** in `backend/main.py` (lines 152-166)

2. **Restart the FastAPI server**:
   ```bash
   cd backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Access the dashboard** at `http://localhost:8000`

### Option B: Run Separately (Development)

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

Access at `http://localhost:5173`

## Step 4: Verify Integration

1. Open the dashboard in your browser
2. Check the connection status (should show "● CONNECTED")
3. Click "Start Detection"
4. Verify detection events appear in real-time
5. Check that statistics update correctly

## Troubleshooting

### "Cannot connect to detection server"

- Verify FastAPI is running: `curl http://localhost:8000/api/health`
- Check the WebSocket URL in `.env` matches your server
- Check CORS settings in `backend/main.py` if frontend is on a different port

### "No detections appearing"

- Check the browser console for errors
- Verify `detection_interface.py` is returning data correctly
- Add print statements in `stream_detections()` to debug

### WebSocket keeps disconnecting

- Check your firewall settings
- Verify the server isn't timing out idle connections
- Check server logs for errors

## Production Deployment

### Using Gunicorn + Uvicorn Workers

```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# Copy built frontend
COPY dist/ ./dist/

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t raptor-detection .
docker run -p 8000:8000 raptor-detection
```

## Security Considerations

1. **Change CORS settings** in production to only allow your domain
2. **Use WSS (WebSocket Secure)** with HTTPS in production
3. **Add authentication** if exposing to the internet
4. **Rate limiting** on the WebSocket endpoint

## Next Steps

- Customize the UI colors and branding
- Add more statistics and visualizations
- Implement alert notifications
- Add historical data storage and analysis
