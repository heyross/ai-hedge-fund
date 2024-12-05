import asyncio
import logging
from typing import Dict, List
from src.base_agent import BaseAgent
from src.agents import MarketDataAgent, QuantitativeAgent, RiskManagementAgent, PortfolioManagementAgent
from src.message_bus import message_bus

logger = logging.getLogger(__name__)

class TradingSystem:
    def __init__(self, user_name=None):
        """
        Initialize the trading system with optional user name
        
        Args:
            user_name (str, optional): Name of the user interacting with the system
        """
        self.user_name = user_name or "Trader"
        self.agents: Dict[str, BaseAgent] = {
            "market_data": MarketDataAgent(user_name=self.user_name),
            "quantitative": QuantitativeAgent(user_name=self.user_name),
            "risk_management": RiskManagementAgent(user_name=self.user_name),
            "portfolio_management": PortfolioManagementAgent(user_name=self.user_name)
        }
        self._running = False
        logger.info(f"Trading system initialized for user: {self.user_name}")

    async def start(self, user_name=None):
        """
        Start all agents with optional user name update
        
        Args:
            user_name (str, optional): Update user name if provided
        """
        if user_name:
            self.user_name = user_name
            # Update user name for all agents
            for agent in self.agents.values():
                await agent.initialize(user_name=self.user_name)

        if self._running:
            logger.warning("Trading system already running")
            return

        self._running = True
        logger.info(f"Starting trading system for {self.user_name}")
        
        # Start each agent
        for agent_type, agent in self.agents.items():
            try:
                await agent.start()
                logger.info(f"Started {agent_type} agent")
            except Exception as e:
                logger.error(f"Error starting {agent_type} agent: {e}")
                continue

        # Announce system start
        await message_bus.publish(
            sender="system",
            message_type="system_message",
            content=f"Trading system started for {self.user_name}. All agents are online and processing data.",
            private=False
        )

    async def stop(self):
        """Stop all agents"""
        if not self._running:
            logger.warning("Trading system not running")
            return

        self._running = False
        logger.info("Stopping trading system")
        
        # Stop each agent
        for agent_type, agent in self.agents.items():
            try:
                await agent.stop()
                logger.info(f"Stopped {agent_type} agent")
            except Exception as e:
                logger.error(f"Error stopping {agent_type} agent: {e}")

        # Announce system stop
        await message_bus.publish(
            sender="system",
            message_type="system_message",
            content="Trading system stopped. All agents are offline.",
            private=False
        )
