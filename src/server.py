from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
import asyncio
from typing import Dict, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.system_running = False
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                
    async def send_private(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending private message: {e}")

manager = ConnectionManager()

# Routes
@app.get("/")
async def get_index():
    return FileResponse(static_path / "index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(id(websocket))
    await manager.connect(websocket, client_id)
    
    try:
        # Send initial system status
        await websocket.send_json({
            "type": "system_status",
            "data": {"running": manager.system_running}
        })
        
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data["type"] == "command":
                if data["action"] == "start":
                    manager.system_running = True
                    await manager.broadcast({
                        "type": "system_status",
                        "data": {"running": True}
                    })
                    # TODO: Start trading system
                    
                elif data["action"] == "stop":
                    manager.system_running = False
                    await manager.broadcast({
                        "type": "system_status",
                        "data": {"running": False}
                    })
                    # TODO: Stop trading system
            
            elif data["type"] == "user_message":
                await manager.broadcast({
                    "type": "group_message",
                    "data": {
                        "sender": "User",
                        "content": data["content"],
                        "timestamp": None,  # Will be set by client
                        "category": "User Input"
                    }
                })
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(client_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
