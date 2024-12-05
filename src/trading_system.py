import asyncio
import logging
from typing import Dict, List
from src.base_agent import BaseAgent
from src.agents import MarketDataAgent, QuantitativeAgent, RiskManagementAgent, PortfolioManagementAgent
from src.message_bus import message_bus

logger = logging.getLogger(__name__)

class TradingSystem:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {
            "market_data": MarketDataAgent(),
            "quantitative": QuantitativeAgent(),
            "risk_management": RiskManagementAgent(),
            "portfolio_management": PortfolioManagementAgent()
        }
        self._running = False
        logger.info("Trading system initialized")

    async def start(self):
        """Start all agents"""
        if self._running:
            logger.warning("Trading system already running")
            return

        self._running = True
        logger.info("Starting trading system")
        
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
            content="Trading system started. All agents are online and processing data.",
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
