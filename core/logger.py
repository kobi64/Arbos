import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "arbos.log"

logger = logging.getLogger("ArbOS")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(message)s"
)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.handlers.clear()
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def startup():
    logger.info("=" * 60)
    logger.info("ArbOS starting...")
    logger.info("Logger initialised successfully.")
    logger.info("=" * 60)

def info(message):
    logger.info(message)

def warning(message):
    logger.warning(message)

def error(message):
    logger.error(message)

def critical(message):
    logger.critical(message)
