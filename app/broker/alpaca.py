from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, StopOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
from app.config import settings
from app.broker.base import Broker
from app.utils.logger import logger
from typing import Dict, Any, List

class AlpacaBroker(Broker):
    def __init__(self):
        # Use settings.ALPACA_PAPER to control paper trading mode
        self.client = TradingClient(settings.ALPACA_API_KEY, settings.ALPACA_SECRET_KEY, paper=settings.ALPACA_PAPER)

    def get_account(self) -> Dict[str, Any]:
        try:
            account = self.client.get_account()
            return {
                "id": str(account.id),
                "cash": float(account.cash),
                "equity": float(account.equity),
                "buying_power": float(account.buying_power),
                "status": account.status
            }
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            return {}

    def get_positions(self) -> List[Dict[str, Any]]:
        try:
            positions = self.client.get_all_positions()
            return [
                {
                    "symbol": p.symbol,
                    "qty": float(p.qty),
                    "market_value": float(p.market_value),
                    "current_price": float(p.current_price),
                    "unrealized_pl": float(p.unrealized_pl),
                    "unrealized_plpc": float(p.unrealized_plpc)
                }
                for p in positions
            ]
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    def submit_order(self, symbol: str, qty: float, side: str, order_type: str, time_in_force: str, limit_price: float = None, stop_price: float = None) -> Dict[str, Any]:
        try:
            side_enum = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            tif_enum = TimeInForce.DAY # Default to DAY
            if time_in_force == "gtc":
                tif_enum = TimeInForce.GTC

            req = None
            if order_type == "market":
                req = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=side_enum,
                    time_in_force=tif_enum
                )
            elif order_type == "limit":
                req = LimitOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=side_enum,
                    time_in_force=tif_enum,
                    limit_price=limit_price
                )

            # Handle other types if needed

            if req:
                order = self.client.submit_order(req)
                logger.info(f"Order submitted: {symbol} {side} {qty} @ {order_type}")
                return {"id": str(order.id), "status": order.status}
            return {}
        except Exception as e:
            logger.error(f"Error submitting order: {e}")
            return {}

    def cancel_all_orders(self):
        try:
            self.client.cancel_orders()
            logger.info("All orders canceled.")
        except Exception as e:
            logger.error(f"Error canceling orders: {e}")

    def close_all_positions(self):
        try:
            self.client.close_all_positions(cancel_orders=True)
            logger.info("All positions closed.")
        except Exception as e:
            logger.error(f"Error closing positions: {e}")
