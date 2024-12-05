import os
from datetime import datetime, timedelta

import pandas as pd
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Initialize Alpaca clients
ALPACA_API_KEY = os.environ.get("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")
ALPACA_PAPER_ENDPOINT = os.environ.get("ALPACA_PAPER_ENDPOINT", "https://paper-api.alpaca.markets")
ALPACA_LIVE_ENDPOINT = os.environ.get("ALPACA_LIVE_ENDPOINT", "https://api.alpaca.markets")

# Initialize clients
data_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
paper_trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)
live_trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=False)

def get_trading_client(paper=True):
    """Get the appropriate trading client based on paper/live mode."""
    return paper_trading_client if paper else live_trading_client

def get_prices(ticker, start_date, end_date):
    """Fetch price data from Alpaca."""
    request_params = StockBarsRequest(
        symbol_or_symbols=[ticker],
        timeframe=TimeFrame.Day,
        start=datetime.strptime(start_date, "%Y-%m-%d"),
        end=datetime.strptime(end_date, "%Y-%m-%d")
    )
    
    bars = data_client.get_stock_bars(request_params)
    df = bars.df
    
    if len(df) == 0:
        raise ValueError(f"No price data returned for {ticker}")
    
    return df

def prices_to_df(prices_df):
    """Convert Alpaca prices to our standard DataFrame format."""
    df = prices_df.copy()
    df.index.name = "Date"
    df.columns = [c.lower() for c in df.columns]
    return df

def get_price_data(ticker, start_date, end_date):
    prices = get_prices(ticker, start_date, end_date)
    return prices_to_df(prices)

def calculate_confidence_level(signals):
    """Calculate confidence level based on the difference between SMAs."""
    sma_diff_prev = abs(signals['sma_5_prev'] - signals['sma_20_prev'])
    sma_diff_curr = abs(signals['sma_5_curr'] - signals['sma_20_curr'])
    diff_change = sma_diff_curr - sma_diff_prev
    # Normalize confidence between 0 and 1
    confidence = min(max(diff_change / signals['current_price'], 0), 1)
    return confidence

def calculate_macd(prices_df):
    ema_12 = prices_df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = prices_df['close'].ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal_line

def calculate_rsi(prices_df, period=14):
    delta = prices_df['close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(prices_df, window=20):
    sma = prices_df['close'].rolling(window).mean()
    std_dev = prices_df['close'].rolling(window).std()
    upper_band = sma + (std_dev * 2)
    lower_band = sma - (std_dev * 2)
    return upper_band, lower_band

def calculate_obv(prices_df):
    obv = [0]
    for i in range(1, len(prices_df)):
        if prices_df['close'].iloc[i] > prices_df['close'].iloc[i - 1]:
            obv.append(obv[-1] + prices_df['volume'].iloc[i])
        elif prices_df['close'].iloc[i] < prices_df['close'].iloc[i - 1]:
            obv.append(obv[-1] - prices_df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    prices_df['OBV'] = obv
    return prices_df['OBV']

def execute_trade(ticker, action, quantity, paper=True, current_price=None):
    """Execute a trade using Alpaca."""
    try:
        # Get the appropriate client
        trading_client = get_trading_client(paper)
        
        # Create market order
        order_side = OrderSide.BUY if action.lower() == "buy" else OrderSide.SELL
        
        order_data = MarketOrderRequest(
            symbol=ticker,
            qty=quantity,
            side=order_side,
            time_in_force=TimeInForce.DAY
        )
        
        # Submit order
        order = trading_client.submit_order(order_data)
        return {
            "status": "submitted",
            "order_id": order.id,
            "side": order_side.value,
            "quantity": quantity,
            "mode": "paper" if paper else "live"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "mode": "paper" if paper else "live"
        }