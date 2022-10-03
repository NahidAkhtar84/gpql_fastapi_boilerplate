from pydantic import BaseModel
import datetime
from pytz import timezone
from logging.config import dictConfig
import logging


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""
    # time_zone = timezone('Asia/Dhaka')
    # current_time = datetime.now(time_zone).strftime('%Y-%m-%d')
    LOGGER_NAME: str = "sts"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "sts": {"handlers": ["default"], "level": LOG_LEVEL},
    }


def log_config():
    dictConfig(LogConfig().dict())
    logger = logging.getLogger("sts")
    return logger
