"""
Logging configuration for Spotify Playlist Exporter
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_level=logging.INFO, log_file=os.path.join(os.path.dirname(__file__), "spotify_exporter.log"), 
                  max_bytes=1024*1024, backup_count=3, console_output=True):
    """
    Set up logging configuration with both file and console output
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Log file name (default: spotify_exporter.log)
        max_bytes: Maximum size of log file before rotation (default: 1MB)
        backup_count: Number of backup files to keep (default: 3)
        console_output: Whether to output logs to console (default: True)
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes, 
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (for headless operation visibility)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name=None):
    """Get a logger instance"""
    return logging.getLogger(name)
