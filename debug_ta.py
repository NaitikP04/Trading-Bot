import pandas as pd
import pandas_ta as ta

df = pd.DataFrame({'close': [100.0] * 20})
bbands = df.ta.bbands(length=20, std=2.0)
print(bbands.columns)
print(bbands.tail())
