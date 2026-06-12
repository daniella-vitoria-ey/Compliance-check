from src.core.logger import get_logger

logger = get_logger("alerts")

def create_alert_tool(message: str):
    logger.warning(message)