from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
import asyncio
from typing import Dict, Set
import logging
from message_bus import message_bus
from trading_system import TradingSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Initialize trading system
trading_system = TradingSystem()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.system_running = False
        
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        # Subscribe to message bus
        await message_bus.subscribe("ui", self._handle_message)
        
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

    async def _handle_message(self, message: dict):
        """Handle messages from the message bus"""
        try:
            await self.broadcast({
                "type": message["type"],
                "data": {
                    "sender": message["sender"],
                    "content": message["content"],
                    "timestamp": message["timestamp"],
                    "private": message["private"]
                }
            })
        except Exception as e:
            logger.error(f"Error handling message bus message: {e}")

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
                if data["action"] == "start" and not manager.system_running:
                    manager.system_running = True
                    await manager.broadcast({
                        "type": "system_status",
                        "data": {"running": True}
                    })
                    await trading_system.start()
                    
                elif data["action"] == "stop" and manager.system_running:
                    manager.system_running = False
                    await manager.broadcast({
                        "type": "system_status",
                        "data": {"running": False}
                    })
                    await trading_system.stop()
            
            elif data["type"] == "user_message":
                # Broadcast user message to all agents through message bus
                await message_bus.publish(
                    sender="user",
                    message_type="user_message",
                    content=data["content"],
                    private=False
                )
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(client_id)

@app.on_event("startup")
async def startup_event():
    # Start message bus
    asyncio.create_task(message_bus.start())

@app.on_event("shutdown")
async def shutdown_event():
    # Stop message bus and trading system
    await message_bus.stop()
    if manager.system_running:
        await trading_system.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)