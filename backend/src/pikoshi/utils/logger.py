import logging

logging.basicConfig(
    level=logging.INFO,  # Set to DEBUG for more detailed logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# NOTE: Consider making a more robust logger that rotates, like this (but not quite):
#  import logging
#  import os
#  from logging.handlers import RotatingFileHandler

#  # Create a logger
#  logger = logging.getLogger(__name__)

#  # Set the log level from environment variable or default to INFO
#  log_level = os.getenv("LOG_LEVEL", "INFO").upper()
#  logger.setLevel(log_level)

#  # Create a formatter that includes time, level, and message
#  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

#  # Console handler
#  console_handler = logging.StreamHandler()
#  console_handler.setLevel(logging.INFO)
#  console_handler.setFormatter(formatter)

#  # File handler with rotation
#  file_handler = RotatingFileHandler(
#  "app.log", maxBytes=10 * 1024 * 1024, backupCount=5
#  )  # 10 MB per file, keep 5 backups
#  file_handler.setLevel(logging.INFO)
#  file_handler.setFormatter(formatter)

#  # Add handlers to the logger
#  logger.addHandler(console_handler)
#  logger.addHandler(file_handler)

# Optional: To log messages in JSON format for structured logging
# Uncomment this section if using structured logging
# import json_log_formatter
# json_formatter = json_log_formatter.JSONFormatter()
# json_handler = logging.StreamHandler()
# json_handler.setFormatter(json_formatter)
# logger.addHandler(json_handler)

#  logger.info("Logger initialized.")
