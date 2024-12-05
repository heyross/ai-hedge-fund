from abc import ABC, abstractmethod
import asyncio
import logging
from typing import Any, Dict
from src.message_bus import message_bus

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, agent_type: str):
        self.name = name
        self.agent_type = agent_type
        self._running = False
        self.state: Dict[str, Any] = {}

    async def start(self):
        """Start the agent"""
        self._running = True
        # Subscribe to messages
        await message_bus.subscribe(self.agent_type, self._handle_message)
        # Start agent's main loop
        asyncio.create_task(self._run())
        logger.info(f"Agent {self.name} started")
        await self._broadcast_status("Running")

    async def stop(self):
        """Stop the agent"""
        self._running = False
        logger.info(f"Agent {self.name} stopped")
        await self._broadcast_status("Stopped")

    async def _run(self):
        """Main agent loop"""
        while self._running:
            try:
                await self.process()
                await asyncio.sleep(1)  # Prevent busy waiting
            except Exception as e:
                logger.error(f"Error in agent {self.name}: {e}")
                await self._broadcast_status(f"Error: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying

    @abstractmethod
    async def process(self):
        """Main processing logic - must be implemented by subclasses"""
        pass

    async def _handle_message(self, message: dict):
        """Handle incoming messages"""
        try:
            if not message["private"] or message["sender"] == self.agent_type:
                await self.handle_message(message)
        except Exception as e:
            logger.error(f"Error handling message in {self.name}: {e}")

    @abstractmethod
    async def handle_message(self, message: dict):
        """Handle a specific message - must be implemented by subclasses"""
        pass

    async def _broadcast_status(self, status: str):
        """Broadcast agent status"""
        await message_bus.publish(
            sender=self.agent_type,
            message_type="agent_status",
            content={"agent": self.name, "status": status},
            private=True
        )

    async def broadcast_thought(self, thought: str):
        """Broadcast agent's current thoughts"""
        await message_bus.publish(
            sender=self.agent_type,
            message_type="agent_thought",
            content=thought,
            private=True
        )

    async def broadcast_message(self, content: Any, message_type: str = "info"):
        """Broadcast a message to all agents"""
        await message_bus.publish(
            sender=self.agent_type,
            message_type=message_type,
            content=content,
            private=False
        )
