import google.generativeai as genai
from app.strategy.base import Strategy, Signal
from app.config import settings
from app.utils.logger import logger
import pandas as pd
import json

class LLMStrategy(Strategy):
    def __init__(self):
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        else:
            self.model = None
            logger.warning("Google API Key not set. LLM Strategy will default to HOLD.")

    def analyze(self, data: pd.DataFrame) -> Signal:
        if not self.model or data.empty:
            return Signal.HOLD

        # Prepare prompt
        # Summarize last 10 candles
        recent_data = data.tail(10).to_string()

        prompt = f"""
        You are a professional stock trader. Analyze the following OHLCV data for a stock (last 10 periods):
        {recent_data}

        Based on the price action, volume, and trend, decide if this is a BUY, SELL, or HOLD for a short-term trade.
        Provide your response in strictly valid JSON format with keys "signal" and "reasoning".
        The "signal" value must be one of: "BUY", "SELL", "HOLD".
        Example: {{"signal": "BUY", "reasoning": "Uptrend with increasing volume"}}
        """

        try:
            response = self.model.generate_content(prompt)
            # Clean response (remove markdown code blocks if any)
            text = response.text.replace("```json", "").replace("```", "").strip()

            # Sometimes model adds extra text, try to find JSON
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                text = text[start:end]

            result = json.loads(text)

            signal_str = result.get("signal", "HOLD").upper()
            # Log reasoning but maybe truncate if too long
            reasoning = result.get('reasoning', 'No reasoning provided')
            logger.info(f"LLM Signal: {signal_str}, Reasoning: {reasoning}")

            if signal_str == "BUY":
                return Signal.BUY
            elif signal_str == "SELL":
                return Signal.SELL
            else:
                return Signal.HOLD

        except Exception as e:
            logger.error(f"LLM Analysis failed: {e}")
            return Signal.HOLD
