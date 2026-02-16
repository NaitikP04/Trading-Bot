from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestTradeRequest, StockSnapshotRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from app.config import settings
from app.data.base import DataProvider
from app.utils.logger import logger
import pandas as pd
from datetime import datetime, timedelta

class AlpacaData(DataProvider):
    def __init__(self):
        self.client = StockHistoricalDataClient(settings.ALPACA_API_KEY, settings.ALPACA_SECRET_KEY)

    def get_bars(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        try:
            tf = TimeFrame.Day
            if timeframe == "1Min":
                tf = TimeFrame.Minute
            elif timeframe == "5Min":
                tf = TimeFrame(5, TimeFrameUnit.Minute)
            elif timeframe == "15Min":
                tf = TimeFrame(15, TimeFrameUnit.Minute)
            elif timeframe == "1H":
                tf = TimeFrame.Hour
            elif timeframe == "1D":
                tf = TimeFrame.Day

            end = datetime.now()
            days_back = 5
            if timeframe == "1D":
                days_back = limit * 2
            elif timeframe == "1H":
                days_back = (limit / 7) + 2

            start = end - timedelta(days=int(days_back))

            req = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=start,
                limit=limit
            )
            bars = self.client.get_stock_bars(req)
            if bars.df.empty:
                return pd.DataFrame()

            df = bars.df
            # Handle MultiIndex (symbol, timestamp)
            if isinstance(df.index, pd.MultiIndex):
                # Check if symbol is in index
                if symbol in df.index.get_level_values(0):
                    df = df.xs(symbol, level=0)
                else:
                    # Try uppercase/lowercase match?
                    # Usually API returns uppercase.
                    pass

            return df
        except Exception as e:
            logger.error(f"Error fetching bars for {symbol}: {e}")
            return pd.DataFrame()

    def get_latest_price(self, symbol: str) -> float:
        try:
            req = StockLatestTradeRequest(symbol_or_symbols=symbol)
            trade = self.client.get_stock_latest_trade(req)
            if symbol in trade:
                return float(trade[symbol].price)
            return 0.0
        except Exception as e:
            logger.error(f"Error fetching latest price for {symbol}: {e}")
            return 0.0

    def get_active_assets(self):
        tickers = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK.B", "LLY", "AVGO",
            "V", "JPM", "XOM", "WMT", "UNH", "MA", "PG", "JNJ", "HD", "MRK",
            "COST", "ABBV", "CVX", "CRM", "BAC", "PEP", "KO", "AMD", "NFLX", "ADBE",
            "TMO", "WFC", "LIN", "MCD", "DIS", "CSCO", "ACN", "ABT", "DHR", "INTC",
            "VZ", "CMCSA", "INTU", "AMGN", "PFE", "TXN", "PM", "IBM", "UBER", "NOW"
        ]

        try:
            req = StockSnapshotRequest(symbol_or_symbols=tickers)
            snapshots = self.client.get_stock_snapshots(req)

            valid = []
            for sym, snap in snapshots.items():
                if snap and snap.daily_bar:
                    valid.append((sym, snap.daily_bar.volume))

            valid.sort(key=lambda x: x[1], reverse=True)

            top_10 = [x[0] for x in valid[:10]]
            logger.info(f"Top 10 Active Assets by Volume: {top_10}")
            return top_10

        except Exception as e:
            logger.error(f"Error fetching active assets (snapshots): {e}")
            return ["SPY", "QQQ", "AAPL", "MSFT", "TSLA", "NVDA", "AMD", "GOOGL", "AMZN", "META"]
