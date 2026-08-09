from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time} | {level} | {message}")
logger.add("app.log", rotation="1 MB", level="DEBUG")

def get_logger():
    return logger