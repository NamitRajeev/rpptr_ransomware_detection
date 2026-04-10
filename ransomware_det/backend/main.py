from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime
from detection_service import DetectionService

app = FastAPI(title="R.A.P.T.O.R Detection API")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global detection service instance
detection_service = None


@app.get("/")
async def root():
    return {
        "message": "R.A.P.T.O.R Detection API",
        "status": "running",
        "endpoints": {
            "websocket": "/ws/detections",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.websocket("/ws/detections")
async def websocket_endpoint(websocket: WebSocket):
    global detection_service
    
    await websocket.accept()
    print(f"[WebSocket] Client connected")
    
    # Send connection confirmation
    await websocket.send_json({
        "type": "connected",
        "message": "Connected to R.A.P.T.O.R detection stream"
    })
    
    # Initialize detection service if not already created
    if detection_service is None:
        detection_service = DetectionService()
    
    try:
        while True:
            # Wait for commands from client
            data = await websocket.receive_text()
            message = json.loads(data)
            command = message.get("command")
            
            if command == "start":
                print("[WebSocket] Starting detection stream...")
                await websocket.send_json({
                    "type": "status",
                    "message": "Detection started"
                })
                
                # Start streaming detections
                async for detection_result in detection_service.stream_detections():
                    # Send detection to frontend
                    await websocket.send_json({
                        "type": "detection",
                        "data": detection_result
                    })
                    
                    # Check if client sent stop command
                    try:
                        data = await asyncio.wait_for(
                            websocket.receive_text(),
                            timeout=0.01
                        )
                        message = json.loads(data)
                        if message.get("command") == "stop":
                            print("[WebSocket] Detection stream paused")
                            detection_service.pause()
                            await websocket.send_json({
                                "type": "status",
                                "message": "Detection paused"
                            })
                            break
                    except asyncio.TimeoutError:
                        # No command received, continue streaming
                        pass
                        
            elif command == "stop":
                print("[WebSocket] Stopping detection stream...")
                detection_service.pause()
                await websocket.send_json({
                    "type": "status",
                    "message": "Detection stopped"
                })
                
            elif command == "reset":
                print("[WebSocket] Resetting detection service...")
                detection_service.reset()
                await websocket.send_json({
                    "type": "status",
                    "message": "Detection reset"
                })
                
    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")
        if detection_service:
            detection_service.pause()
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
