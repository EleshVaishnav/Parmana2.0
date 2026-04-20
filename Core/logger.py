import logging
import os
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Create a custom logger
logger = logging.getLogger("Deep Claw")
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = RotatingFileHandler("logs/deep claw.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")

c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
if not logger.handlers:
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
