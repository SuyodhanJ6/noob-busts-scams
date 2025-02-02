# import logging
# import os
# from datetime import datetime

# # Creating logs directory to store log in files
# LOG_DIR = "logs"
# LOG_DIR = os.path.join(os.getcwd(), LOG_DIR)

# # Creating LOG_DIR if it does not exists.
# os.makedirs(LOG_DIR, exist_ok=True)


# # Creating file name for log file based on current timestamp
# CURRENT_TIME_STAMP = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
# file_name = f"log_{CURRENT_TIME_STAMP}.log"

# # Creating file path for projects.
# log_file_path = os.path.join(LOG_DIR, file_name)


# logging.basicConfig(
#     filename=log_file_path,
#     filemode="w",
#     format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO,
# )
from datetime import datetime
import logging
import os
import sys
from typing import Optional

from loguru import logger

class CustomLogger:
    @staticmethod
    def setup_logger(log_level: str = "INFO", log_file: Optional[str] = None):
        """Configure logger with custom format and handlers"""
        
        # Remove default handlers
        logger.remove()
        
        # Format for logs
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Add console handler
        logger.add(
            sys.stdout,
            format=log_format,
            level=log_level,
            colorize=True
        )
        
        # Add file handler if specified
        if log_file:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            
            file_path = os.path.join(
                log_dir,
                f"{log_file}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            
            logger.add(
                file_path,
                format=log_format,
                level=log_level,
                rotation="500 MB",
                retention="10 days"
            )
        
        # Intercept standard library logging
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

class InterceptHandler(logging.Handler):
    """Intercepts standard library logging and redirects to loguru"""
    
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
            
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
            
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

# Initialize logger
logger = logger.bind(service="noob-busts-scams")
