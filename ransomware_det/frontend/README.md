# R.A.P.T.O.R - Real-time Adaptive Protection Through Optimized Recognition

A real-time intrusion detection dashboard powered by a hybrid RF + LSTM detection engine with FastAPI backend and React frontend.

## Features

- 🔴 **Real-time Detection Streaming** via WebSocket
- 🤖 **Hybrid ML Models** - Random Forest + LSTM
- 📊 **Live Statistics Dashboard** - Track detections, attacks, and ransomware
- 🎨 **Modern UI** - Beautiful gradient design with real-time updates
- 🔄 **Auto-reconnection** - Handles connection drops gracefully
- ⚡ **Fast & Responsive** - Built with React + Vite + FastAPI

## Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
npm install
```

### 2. Run Development Servers

**Backend (Terminal 1):**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (Terminal 2):**
```bash
npm run dev
```

### 3. Open Dashboard

Visit `http://localhost:5173` and click "Start Detection"

## Project Structure

```
raptor/
├── backend/
│   ├── main.py                 # FastAPI app with WebSocket
│   ├── detection_interface.py  # Detection engine interface
│   └── requirements.txt        # Python dependencies
├── src/
│   ├── Dashboard.tsx           # Main dashboard component
│   └── ...
├── .env                        # Environment configuration
└── DEPLOYMENT.md               # Full deployment guide
```

## Integrating Your Detection Engine

See `backend/detection_interface.py` - replace the `simulate_detection()` method with your actual RF + LSTM model predictions.

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete deployment instructions.

## Tech Stack

- **Frontend:** React 19, TypeScript, Vite, TailwindCSS
- **Backend:** FastAPI, WebSockets, Uvicorn
- **ML:** Random Forest + LSTM (your models)

## License

MIT
