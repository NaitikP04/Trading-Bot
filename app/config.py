import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Alpaca Settings
    ALPACA_API_KEY: str = "PK_DUMMY_KEY"
    ALPACA_SECRET_KEY: str = "sk_dummy_secret"
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets" # Default to paper
    ALPACA_DATA_URL: str = "https://data.alpaca.markets"
    ALPACA_PAPER: bool = True # Set to False for Live Trading

    # Strategy Settings
    STRATEGY_NAME: str = "bollinger" # or "llm"
    TRADING_SYMBOL: str = "" # If empty, bot picks stocks
    TIMEFRAME: str = "15Min" # 5Min, 15Min, 1H

    # Risk Management
    MAX_DAILY_LOSS: float = 100.0
    MAX_POSITION_SIZE: float = 1000.0 # in dollars
    STOP_LOSS_PCT: float = 0.02 # 2%
    TAKE_PROFIT_PCT: float = 0.04 # 4%

    # LLM Settings (Gemini)
    GOOGLE_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash" # or gemini-pro

    # Data Settings
    ACTIVE_ASSET_CANDIDATES: list[str] = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK.B", "LLY", "AVGO",
        "V", "JPM", "XOM", "WMT", "UNH", "MA", "PG", "JNJ", "HD", "MRK",
        "COST", "ABBV", "CVX", "CRM", "BAC", "PEP", "KO", "AMD", "NFLX", "ADBE",
        "TMO", "WFC", "LIN", "MCD", "DIS", "CSCO", "ACN", "ABT", "DHR", "INTC",
        "VZ", "CMCSA", "INTU", "AMGN", "PFE", "TXN", "PM", "IBM", "UBER", "NOW"
    ]
    ACTIVE_ASSET_FALLBACK: list[str] = ["SPY", "QQQ", "AAPL", "MSFT", "TSLA", "NVDA", "AMD", "GOOGL", "AMZN", "META"]

    # Discord Integration (Optional)
    DISCORD_WEBHOOK_URL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
