from app.strategy.base import Strategy, Signal
from app.utils.logger import logger
import pandas as pd
import pandas_ta as ta

class BollingerStrategy(Strategy):
    def __init__(self, length: int = 20, std: float = 2.0):
        self.length = length
        self.std = std

    def analyze(self, data: pd.DataFrame) -> Signal:
        if data.empty or len(data) < self.length:
            return Signal.HOLD

        # Copy data to avoid SettingWithCopyWarning
        df = data.copy()

        # Check column names case
        if 'close' not in df.columns and 'Close' in df.columns:
            df.rename(columns={'Close': 'close'}, inplace=True)

        try:
            # calculate bbands
            # columns: BBL_..., BBM_..., BBU_...
            bbands = df.ta.bbands(length=self.length, std=self.std)
            if bbands is None or bbands.empty:
                return Signal.HOLD

            # Find columns dynamically
            bbl_col = next((c for c in bbands.columns if c.startswith("BBL")), None)
            bbu_col = next((c for c in bbands.columns if c.startswith("BBU")), None)

            if not bbl_col or not bbu_col:
                logger.error(f"Strategy Error: Could not find Bollinger Columns in {bbands.columns}")
                return Signal.HOLD

            # Get latest values
            latest_bb = bbands.iloc[-1]
            latest_close = df.iloc[-1]['close']

            bbl = latest_bb[bbl_col]
            bbu = latest_bb[bbu_col]

            # Ensure not NaN
            if pd.isna(bbl) or pd.isna(bbu) or pd.isna(latest_close):
                return Signal.HOLD

            if latest_close < bbl:
                return Signal.BUY
            elif latest_close > bbu:
                return Signal.SELL

        except Exception as e:
            logger.error(f"Strategy Error: {e}")
            return Signal.HOLD

        return Signal.HOLD
