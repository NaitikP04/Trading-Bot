from abc import ABC, abstractmethod
from typing import List, Dict, Any

class Broker(ABC):
    @abstractmethod
    def get_account(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def submit_order(self, symbol: str, qty: float, side: str, order_type: str, time_in_force: str, limit_price: float = None, stop_price: float = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def cancel_all_orders(self):
        pass

    @abstractmethod
    def close_all_positions(self):
        pass
