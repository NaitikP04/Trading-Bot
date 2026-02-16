from abc import ABC, abstractmethod
import pandas as pd
from typing import List

class DataProvider(ABC):
    @abstractmethod
    def get_bars(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_latest_price(self, symbol: str) -> float:
        pass

    @abstractmethod
    def get_active_assets(self) -> List[str]:
        """Returns a list of active assets (e.g., top gainers/losers/high volume)"""
        pass
