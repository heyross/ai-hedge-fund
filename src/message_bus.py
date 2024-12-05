import asyncio
from typing import Dict, List, Callable, Awaitable, Any
import json
import logging
from datetime import datetime
from src.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {
            'market_data': [],
            'quantitative': [],
            'risk_management': [],
            'portfolio_management': [],
            'ui': []
        }
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        logger.info("MessageBus initialized")

    async def publish(self, sender: str, message_type: str, content: Any, private: bool = False):
        """Publish a message to the bus"""
        message = {
            "sender": sender,
            "type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "private": private
        }
        logger.debug(f"Publishing message: {message}")
        await self.message_queue.put(message)

    async def subscribe(self, channel: str, callback: Callable):
        """
        Subscribe to a specific channel
        Normalize channel name to match predefined channels
        """
        # Normalize channel names
        normalized_channel = self._normalize_channel(channel)
        
        if normalized_channel not in self.subscribers:
            logger.warning(f"Unknown channel: {normalized_channel}")
            return
        
        self.subscribers[normalized_channel].append(callback)
        logger.debug(f"Added subscriber for {normalized_channel}. Total subscribers: {len(self.subscribers[normalized_channel])}")

    def _normalize_channel(self, channel: str) -> str:
        """
        Normalize channel names to match predefined channels
        """
        channel = channel.lower().replace(' ', '').replace('agent', '')
        channel_map = {
            'marketdata': 'market_data',
            'quantitative': 'quantitative',
            'riskmanagement': 'risk_management',
            'portfoliomanagement': 'portfolio_management'
        }
        return channel_map.get(channel, channel)

    async def start(self):
        """Start processing messages"""
        logger.info("Starting message bus")
        self._running = True
        while self._running:
            try:
                message = await self.message_queue.get()
                logger.debug(f"Processing message: {message}")
                tasks = []
                
                # Determine recipients based on message privacy
                if message["private"]:
                    # Private messages go to UI and the specific agent
                    recipients = ["ui"]
                    if message["sender"] in self.subscribers:
                        recipients.append(message["sender"])
                    logger.debug(f"Private message recipients: {recipients}")
                else:
                    # Public messages go to everyone
                    recipients = list(self.subscribers.keys())
                    logger.debug(f"Public message recipients: {recipients}")

                # Create tasks for each subscriber
                for agent_type in recipients:
                    subscriber_count = len(self.subscribers[agent_type])
                    logger.debug(f"Sending to {agent_type} ({subscriber_count} subscribers)")
                    for callback in self.subscribers[agent_type]:
                        tasks.append(asyncio.create_task(self._safe_callback(callback, message)))

                if tasks:
                    await asyncio.gather(*tasks)
                    logger.debug(f"Completed {len(tasks)} message deliveries")
                
                self.message_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)

    async def _safe_callback(self, callback: Callable, message: dict):
        """Safely execute a callback with error handling"""
        try:
            await callback(message)
        except Exception as e:
            logger.error(f"Error in subscriber callback: {e}", exc_info=True)

    async def stop(self):
        """Stop processing messages"""
        logger.info("Stopping message bus")
        self._running = False
        # Process remaining messages
        remaining = self.message_queue.qsize()
        if remaining > 0:
            logger.info(f"Processing {remaining} remaining messages")
        while not self.message_queue.empty():
            await asyncio.sleep(0.1)
        logger.info("Message bus stopped")

# Global message bus instance
message_bus = MessageBus()
