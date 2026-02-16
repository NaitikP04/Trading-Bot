from abc import ABC, abstractmethod
import pandas as pd
from enum import Enum

class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class Strategy(ABC):
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Signal:
        pass
