from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from app.config import settings
from app.utils.logger import logger
from app.broker.alpaca import AlpacaBroker
from app.data.alpaca import AlpacaData
from app.strategy.bollinger import BollingerStrategy
from app.strategy.llm_strategy import LLMStrategy
from app.risk.manager import RiskManager
from app.strategy.base import Signal

# Initialize components
broker = AlpacaBroker()
data_provider = AlpacaData()
risk_manager = RiskManager()

# Select Strategy
if settings.STRATEGY_NAME == "llm":
    strategy = LLMStrategy()
else:
    strategy = BollingerStrategy()

running = True

async def trading_loop():
    logger.info("Starting Trading Loop...")
    # Initialize equity
    account = broker.get_account()
    if account:
        risk_manager.set_initial_equity(float(account.get("equity", 0.0)))

    while running:
        try:
            # 1. Get Account Info
            account = broker.get_account()
            if not risk_manager.can_trade(account):
                logger.warning("Risk checks failed. Stopping trading for now.")
                await asyncio.sleep(60)
                continue

            # 2. Get Candidates
            symbols = []
            if settings.STRATEGY_NAME == "llm":
                 # If LLM, utilize active assets to let it 'pick'
                 symbols = data_provider.get_active_assets()
            elif settings.TRADING_SYMBOL:
                symbols = [settings.TRADING_SYMBOL]
            else:
                symbols = data_provider.get_active_assets()

            for symbol in symbols:
                logger.info(f"Analyzing {symbol}...")

                # 3. Get Data
                bars = data_provider.get_bars(symbol, settings.TIMEFRAME, limit=50)

                if bars.empty:
                    logger.warning(f"No data for {symbol}")
                    continue

                # 4. Analyze
                signal = strategy.analyze(bars)
                logger.info(f"Signal for {symbol}: {signal}")

                # 5. Execute
                if signal == Signal.BUY:
                    # Check if already holding?
                    positions = broker.get_positions()
                    has_position = any(p['symbol'] == symbol for p in positions)

                    if not has_position:
                        # Calculate quantity based on position size
                        price = data_provider.get_latest_price(symbol)
                        if price > 0:
                            qty = int(settings.MAX_POSITION_SIZE / price)
                            if qty > 0:
                                if risk_manager.validate_order(symbol, qty, price, account):
                                    broker.submit_order(symbol, qty, "buy", "market", "day")
                            else:
                                logger.warning(f"Price {price} too high for max position size {settings.MAX_POSITION_SIZE}")

                elif signal == Signal.SELL:
                    # Check if we have a position to sell
                    positions = broker.get_positions()
                    has_position = any(p['symbol'] == symbol for p in positions)
                    if has_position:
                        # Close position
                        pos = next(p for p in positions if p['symbol'] == symbol)
                        qty = abs(float(pos['qty'])) # Ensure positive
                        broker.submit_order(symbol, qty, "sell", "market", "day")

            # Sleep based on timeframe or fixed interval
            logger.info("Sleeping for 60 seconds...")
            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Error in trading loop: {e}")
            await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(trading_loop())
    yield
    # Shutdown
    global running
    running = False
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Trading loop cancelled")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def health_check():
    return {"status": "running", "strategy": settings.STRATEGY_NAME}

@app.get("/account")
def get_account_info():
    return broker.get_account()

@app.get("/positions")
def get_positions():
    return broker.get_positions()
