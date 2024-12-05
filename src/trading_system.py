import asyncio
import logging
from typing import Dict, List
from base_agent import BaseAgent
from agents import MarketDataAgent, QuantitativeAgent, RiskManagementAgent, PortfolioManagementAgent

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

    async def start(self):
        """Start all agents"""
        self._running = True
        start_tasks = [agent.start() for agent in self.agents.values()]
        await asyncio.gather(*start_tasks)
        logger.info("Trading system started")

    async def stop(self):
        """Stop all agents"""
        self._running = False
        stop_tasks = [agent.stop() for agent in self.agents.values()]
        await asyncio.gather(*stop_tasks)
        logger.info("Trading system stopped")
