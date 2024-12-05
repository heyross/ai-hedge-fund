import asyncio
import logging
from typing import Dict, List
from src.base_agent import BaseAgent
from src.agents import MarketDataAgent, QuantitativeAgent, RiskManagementAgent, PortfolioManagementAgent

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
            return

        self._running = True
        logger.info("Starting trading system")
        
        # Initialize agents
        for agent_type, agent in self.agents.items():
            try:
                # Subscribe agent to message bus
                await message_bus.subscribe(agent_type, agent.handle_message)
                # Start agent processing loop
                asyncio.create_task(self._run_agent(agent))
                logger.info(f"Started {agent_type} agent")
            except Exception as e:
                logger.error(f"Error starting {agent_type} agent: {e}")

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
            return

        self._running = False
        logger.info("Stopping trading system")
        
        # Announce system stop
        await message_bus.publish(
            sender="system",
            message_type="system_message",
            content="Trading system stopping. All agents will be taken offline.",
            private=False
        )

    async def _run_agent(self, agent):
        """Run an agent's processing loop"""
        while self._running:
            try:
                await agent.process()
                await asyncio.sleep(1)  # Prevent tight loop
            except Exception as e:
                logger.error(f"Error in agent {agent.name}: {e}")
                await asyncio.sleep(5)  # Back off on error
