# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configures a centralized logging system.
    """
    # Create the main logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console handler for real-time output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler for saving logs to a file
    # Rotates log file to prevent it from getting too large
    file_handler = RotatingFileHandler(
        'pipeline.log',
        maxBytes=1024 * 1024 * 5,  # 5 MB
        backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Add both handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# The configuration is a function so we can call it at the start of each script.