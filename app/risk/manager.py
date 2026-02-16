from app.config import settings
from app.utils.logger import logger
from typing import Dict, Any

class RiskManager:
    def __init__(self):
        self.max_daily_loss = settings.MAX_DAILY_LOSS
        self.max_position_size = settings.MAX_POSITION_SIZE
        self.initial_equity = None # Will set on first run

    def set_initial_equity(self, equity: float):
        if self.initial_equity is None:
            self.initial_equity = equity
            logger.info(f"Initial Equity set to: ${equity}")

    def can_trade(self, account_info: Dict[str, Any]) -> bool:
        if not account_info:
            return False

        current_equity = float(account_info.get("equity", 0.0))

        # Initialize if not set
        if self.initial_equity is None:
            self.set_initial_equity(current_equity)

        # Check Max Daily Loss
        # If equity drops below initial - max_loss
        loss = self.initial_equity - current_equity
        if loss > self.max_daily_loss:
            logger.warning(f"Risk Trigger: Max Daily Loss exceeded (${loss:.2f} > ${self.max_daily_loss})")
            return False

        return True

    def validate_order(self, symbol: str, qty: float, price: float, account_info: Dict[str, Any]) -> bool:
        # Check Buying Power
        buying_power = float(account_info.get("buying_power", 0.0))
        cost = qty * price

        if cost > buying_power:
            logger.warning(f"Risk Trigger: Insufficient Buying Power for {symbol} (Cost: ${cost:.2f}, BP: ${buying_power:.2f})")
            return False

        # Check Max Position Size
        if cost > self.max_position_size:
            logger.warning(f"Risk Trigger: Max Position Size exceeded for {symbol} (Cost: ${cost:.2f} > ${self.max_position_size})")
            return False

        return True
