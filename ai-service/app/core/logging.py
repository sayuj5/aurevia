import logging
import sys
from .config import settings

def setup_logging():
    level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO
    
    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format=log_format,
    )
    
    # Disable noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return logging.getLogger(settings.APP_NAME)

logger = setup_logging()
