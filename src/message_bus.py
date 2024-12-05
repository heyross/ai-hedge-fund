import asyncio
from typing import Dict, List, Callable, Awaitable, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[dict], Awaitable[None]]]] = {
            "market_data": [],
            "quantitative": [],
            "risk_management": [],
            "portfolio_management": [],
            "ui": []
        }
        self._running = False
        self.message_queue = asyncio.Queue()

    async def publish(self, sender: str, message_type: str, content: Any, private: bool = False):
        """Publish a message to the bus"""
        message = {
            "sender": sender,
            "type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "private": private
        }
        await self.message_queue.put(message)

    async def subscribe(self, agent_type: str, callback: Callable[[dict], Awaitable[None]]):
        """Subscribe to messages"""
        if agent_type in self.subscribers:
            self.subscribers[agent_type].append(callback)
        else:
            logger.warning(f"Unknown agent type: {agent_type}")

    async def start(self):
        """Start processing messages"""
        self._running = True
        while self._running:
            try:
                message = await self.message_queue.get()
                tasks = []
                
                # Determine recipients based on message privacy
                if message["private"]:
                    # Private messages go to UI and the specific agent
                    recipients = ["ui"]
                    if message["sender"] in self.subscribers:
                        recipients.append(message["sender"])
                else:
                    # Public messages go to everyone
                    recipients = list(self.subscribers.keys())

                # Create tasks for each subscriber
                for agent_type in recipients:
                    for callback in self.subscribers[agent_type]:
                        tasks.append(asyncio.create_task(callback(message)))

                if tasks:
                    await asyncio.gather(*tasks)
                
                self.message_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def stop(self):
        """Stop processing messages"""
        self._running = False
        # Process remaining messages
        while not self.message_queue.empty():
            await asyncio.sleep(0.1)

# Global message bus instance
message_bus = MessageBus()
