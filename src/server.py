from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
import json
import asyncio
from typing import Dict
import logging
from src.message_bus import message_bus
from src.trading_system import TradingSystem
from datetime import datetime
from src.logging_config import setup_logging

# Initialize logging
setup_logging()
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
        # Subscribe to message bus on initialization
        asyncio.create_task(self._subscribe_to_message_bus())

    async def _subscribe_to_message_bus(self):
        try:
            logger.info("ConnectionManager subscribing to message bus")
            # Subscribe to UI channel with the _handle_message method
            await message_bus.subscribe(callback=self._handle_message, channel='ui')
            logger.info("Successfully subscribed to message bus")
        except Exception as e:
            logger.error(f"Error subscribing to message bus: {e}")

    async def connect(self, websocket: WebSocket, client_id: str):
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            logger.info(f"Client {client_id} connected")
        except Exception as e:
            logger.error(f"Error accepting WebSocket connection: {e}")
            raise

    async def disconnect(self, client_id: str):
        try:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
                logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting client {client_id}: {e}")

    async def broadcast(self, message: dict):
        try:
            for client_id, connection in list(self.active_connections.items()):
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to client {client_id}: {e}")
                    await self.disconnect(client_id)
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")

    async def send_private(self, client_id: str, message: dict):
        try:
            if client_id in self.active_connections:
                await self.active_connections[client_id].send_json(message)
        except Exception as e:
            logger.error(f"Error sending private message to client {client_id}: {e}")
            await self.disconnect(client_id)

    async def _handle_message(self, message: dict):
        try:
            logger.debug(f"Handling message from bus: {message}")
            # Broadcast all messages from the bus to WebSocket clients
            await self.broadcast(message)
        except Exception as e:
            logger.error(f"Error handling message from bus: {e}")

manager = ConnectionManager()

# Routes
@app.get("/")
async def get_index():
    try:
        return FileResponse(static_path / "index.html")
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return HTMLResponse("Error loading application")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = str(id(websocket))
    try:
        await manager.connect(websocket, client_id)
        logger.info(f"WebSocket connection established for client {client_id}")
        
        # Send initial system status
        await websocket.send_json({
            "type": "system_status",
            "data": {"running": manager.system_running}
        })
        
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                logger.debug(f"Received WebSocket message: {data}")
                
                # Handle test connection message
                if data.get("type") == "test_connection":
                    logger.info(f"Test connection received from client {client_id}")
                    await websocket.send_json({
                        "type": "test_connection_response",
                        "message": "WebSocket connection verified successfully"
                    })
                    continue
                
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
                    logger.info(f"User message: {data['content']}")
                    # Echo back to all clients including sender
                    await manager.broadcast({
                        "type": "user_message",
                        "sender": "You",
                        "content": data["content"],
                        "timestamp": datetime.now().isoformat(),
                        "category": "user"
                    })
                    
                    # Forward to message bus for agent processing
                    try:
                        await message_bus.publish(
                            sender="user",
                            message_type="user_message",
                            content=data["content"],
                            private=False
                        )
                    except Exception as e:
                        logger.error(f"Error publishing user message to message bus: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": "Failed to process your message. Please try again."
                        })
            
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from client {client_id}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid message format"
                })
            except Exception as e:
                logger.error(f"Error processing message from client {client_id}: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": "An error occurred processing your request"
                })
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        await manager.disconnect(client_id)

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
