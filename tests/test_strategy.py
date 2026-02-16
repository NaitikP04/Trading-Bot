import pandas as pd
from app.strategy.bollinger import BollingerStrategy
from app.strategy.base import Signal

def test_bollinger_buy():
    # Create data where price < lower band
    # 20 periods of 100
    data = pd.DataFrame({
        'close': [100.0] * 20
    })
    # Make the last one drop significantly (to 80)
    # Mean ~ 99. Std ~ small.
    # Actually if 19 items are 100, and 1 item is 80.
    # Mean = (1900+80)/20 = 99.
    # Std dev will be small.
    # Lower band will be near 99.
    # 80 is well below.
    data.iloc[-1, data.columns.get_loc('close')] = 80.0

    strategy = BollingerStrategy(length=20, std=2.0)
    signal = strategy.analyze(data)

    assert signal == Signal.BUY

def test_bollinger_sell():
    # Create data where price > upper band
    data = pd.DataFrame({
        'close': [100.0] * 20
    })
    data.iloc[-1, data.columns.get_loc('close')] = 120.0

    strategy = BollingerStrategy(length=20, std=2.0)
    signal = strategy.analyze(data)

    assert signal == Signal.SELL

def test_bollinger_hold():
    data = pd.DataFrame({
        'close': [100.0] * 20
    })
    strategy = BollingerStrategy(length=20, std=2.0)
    signal = strategy.analyze(data)
    # Price = 100. Bands = 100 (if std=0).
    # pandas-ta might return NaN if std=0 or handle it.
    # But 100 is not < BBL and not > BBU.
    assert signal == Signal.HOLD
