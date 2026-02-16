import requests
import json
from app.config import settings
from app.utils.logger import logger

def send_discord_alert(message: str, level: str = "info"):
    """
    Send a message to Discord via Webhook.
    """
    if not settings.DISCORD_WEBHOOK_URL:
        # Only log warning once or just debug to avoid spamming logs if not configured
        logger.debug("Discord Webhook URL not set. Skipping alert.")
        return

    color = 0x3498db # Blue (Info)
    if level == "error":
        color = 0xe74c3c # Red
    elif level == "warning":
        color = 0xf1c40f # Yellow
    elif level == "success":
        color = 0x2ecc71 # Green

    payload = {
        "embeds": [
            {
                "title": f"Trading Bot Alert: {level.upper()}",
                "description": message,
                "color": color
            }
        ]
    }

    try:
        response = requests.post(settings.DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send Discord alert: {e}")
