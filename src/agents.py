from typing import Dict, Any
import asyncio
import logging
from datetime import datetime
from base_agent import BaseAgent
from tools import calculate_bollinger_bands, calculate_macd, calculate_obv, calculate_rsi, get_prices, prices_to_df
from langchain_openai.chat_models import ChatOpenAI
import time
import json

logger = logging.getLogger(__name__)

class MarketDataAgent(BaseAgent):
    def __init__(self):
        super().__init__("Market Data Agent", "market_data")
        self.last_update = 0
        self.update_interval = 60  # Update every 60 seconds

    async def process(self):
        if time.time() - self.last_update < self.update_interval:
            return

        try:
            await self.broadcast_thought("Fetching market data...")
            prices = get_prices(self.state.get("ticker", "AAPL"), 
                              self.state.get("start_date"),
                              self.state.get("end_date"))
            
            if prices is not None:
                await self.broadcast_message({
                    "prices": prices.to_dict(),
                    "timestamp": datetime.now().isoformat()
                }, "market_data")
                
                self.last_update = time.time()
                await self.broadcast_thought("Market data updated successfully")
            
        except Exception as e:
            logger.error(f"Error in MarketDataAgent: {e}")
            await self.broadcast_thought(f"Error: {str(e)}")

    async def handle_message(self, message: dict):
        if message["type"] == "user_message":
            content = message["content"]
            if isinstance(content, dict) and "ticker" in content:
                self.state["ticker"] = content["ticker"]
                self.last_update = 0  # Force update on ticker change

class QuantitativeAgent(BaseAgent):
    def __init__(self):
        super().__init__("Quantitative Agent", "quantitative")
        self.last_analysis = 0
        self.analysis_interval = 300  # Analyze every 5 minutes

    async def process(self):
        if time.time() - self.last_analysis < self.analysis_interval:
            return

        try:
            await self.broadcast_thought("Analyzing market data...")
            if "prices" in self.state:
                df = prices_to_df(self.state["prices"])
                
                # Calculate technical indicators
                bb = calculate_bollinger_bands(df)
                macd = calculate_macd(df)
                rsi = calculate_rsi(df)
                obv = calculate_obv(df)
                
                # Generate signals
                signals = []
                
                # MACD signal
                macd_diff = macd["macd"] - macd["signal"]
                signals.append("bullish" if macd_diff.iloc[-1] > 0 else "bearish")
                
                # RSI signal
                rsi_value = rsi.iloc[-1]
                signals.append("bullish" if rsi_value < 30 else "bearish" if rsi_value > 70 else "neutral")
                
                # Bollinger Bands signal
                price = df["close"].iloc[-1]
                bb_position = (price - bb["middle"]) / (bb["upper"] - bb["middle"])
                signals.append("bullish" if bb_position < -1 else "bearish" if bb_position > 1 else "neutral")
                
                analysis = {
                    "signals": signals,
                    "indicators": {
                        "bollinger_bands": bb.to_dict(),
                        "macd": macd.to_dict(),
                        "rsi": rsi.to_dict(),
                        "obv": obv.to_dict(),
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.broadcast_message(analysis, "technical_analysis")
                self.last_analysis = time.time()
                await self.broadcast_thought("Technical analysis completed")
                
        except Exception as e:
            logger.error(f"Error in QuantitativeAgent: {e}")
            await self.broadcast_thought(f"Error: {str(e)}")

    async def handle_message(self, message: dict):
        if message["type"] == "market_data":
            self.state["prices"] = message["content"]["prices"]
            self.last_analysis = 0  # Force analysis on new data

class RiskManagementAgent(BaseAgent):
    def __init__(self):
        super().__init__("Risk Management Agent", "risk_management")
        self.last_assessment = 0
        self.assessment_interval = 300  # Assess every 5 minutes

    async def process(self):
        if time.time() - self.last_assessment < self.assessment_interval:
            return

        try:
            await self.broadcast_thought("Assessing portfolio risk...")
            if "technical_analysis" in self.state:
                analysis = self.state["technical_analysis"]
                signals = analysis["signals"]
                
                # Simple risk scoring
                bullish_count = signals.count("bullish")
                bearish_count = signals.count("bearish")
                
                if bearish_count > bullish_count:
                    risk_level = "high"
                    max_position = 0.05  # 5% max position
                elif bullish_count > bearish_count:
                    risk_level = "low"
                    max_position = 0.15  # 15% max position
                else:
                    risk_level = "medium"
                    max_position = 0.1   # 10% max position
                
                assessment = {
                    "risk_level": risk_level,
                    "max_position_size": max_position,
                    "stop_loss": 0.02,  # 2% stop loss
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.broadcast_message(assessment, "risk_assessment")
                self.last_assessment = time.time()
                await self.broadcast_thought(f"Risk assessment completed: {risk_level} risk")
                
        except Exception as e:
            logger.error(f"Error in RiskManagementAgent: {e}")
            await self.broadcast_thought(f"Error: {str(e)}")

    async def handle_message(self, message: dict):
        if message["type"] == "technical_analysis":
            self.state["technical_analysis"] = message["content"]
            self.last_assessment = 0  # Force assessment on new analysis

class PortfolioManagementAgent(BaseAgent):
    def __init__(self):
        super().__init__("Portfolio Management Agent", "portfolio_management")
        self.last_decision = 0
        self.decision_interval = 300  # Make decisions every 5 minutes

    async def process(self):
        if time.time() - self.last_decision < self.decision_interval:
            return

        try:
            await self.broadcast_thought("Making trading decisions...")
            if all(k in self.state for k in ["technical_analysis", "risk_assessment"]):
                analysis = self.state["technical_analysis"]
                risk = self.state["risk_assessment"]
                
                signals = analysis["signals"]
                bullish_count = signals.count("bullish")
                bearish_count = signals.count("bearish")
                
                if bullish_count > bearish_count and risk["risk_level"] != "high":
                    action = "buy"
                    reason = "Bullish signals with acceptable risk"
                elif bearish_count > bullish_count or risk["risk_level"] == "high":
                    action = "sell"
                    reason = "Bearish signals or high risk"
                else:
                    action = "hold"
                    reason = "Mixed signals or neutral risk"
                
                decision = {
                    "action": action,
                    "reason": reason,
                    "max_position_size": risk["max_position_size"],
                    "stop_loss": risk["stop_loss"],
                    "timestamp": datetime.now().isoformat()
                }
                
                await self.broadcast_message(decision, "trading_decision")
                self.last_decision = time.time()
                await self.broadcast_thought(f"Trading decision made: {action}")
                
        except Exception as e:
            logger.error(f"Error in PortfolioManagementAgent: {e}")
            await self.broadcast_thought(f"Error: {str(e)}")

    async def handle_message(self, message: dict):
        if message["type"] == "technical_analysis":
            self.state["technical_analysis"] = message["content"]
        elif message["type"] == "risk_assessment":
            self.state["risk_assessment"] = message["content"]
            self.last_decision = 0  # Force decision on new risk assessment

# Define the new workflow
workflow = StateGraph()

# Add nodes
workflow.add_node("market_data_agent", MarketDataAgent())
workflow.add_node("quant_agent", QuantitativeAgent())
workflow.add_node("risk_management_agent", RiskManagementAgent())
workflow.add_node("portfolio_management_agent", PortfolioManagementAgent())

# Define the workflow
workflow.set_entry_point("market_data_agent")
workflow.add_edge("market_data_agent", "quant_agent")
workflow.add_edge("quant_agent", "risk_management_agent")
workflow.add_edge("risk_management_agent", "portfolio_management_agent")

app = workflow.compile()

# Add this at the bottom of the file
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the hedge fund trading system')
    parser.add_argument('--ticker', type=str, required=True, help='Stock ticker symbol')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD). Defaults to 3 months before end date')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD). Defaults to today')
    parser.add_argument('--show-reasoning', action='store_true', help='Show reasoning from each agent')
    
    args = parser.parse_args()
    
    # Validate dates if provided
    if args.start_date:
        try:
            datetime.strptime(args.start_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Start date must be in YYYY-MM-DD format")
    
    if args.end_date:
        try:
            datetime.strptime(args.end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("End date must be in YYYY-MM-DD format")
    
    # Sample portfolio - you might want to make this configurable too
    portfolio = {
        "cash": 100000.0,  # $100,000 initial cash
        "stock": 0         # No initial stock position
    }
    
    result = app.invoke({
        "market_data_agent": {
            "ticker": args.ticker,
            "start_date": args.start_date,
            "end_date": args.end_date
        },
        "quant_agent": {},
        "risk_management_agent": {},
        "portfolio_management_agent": {}
    })
    print("\nFinal Result:")
    print(result)