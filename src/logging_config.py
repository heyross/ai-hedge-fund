import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import sys
import traceback

def setup_logging():
    """Configure the logging system with enhanced error handling and organization."""
    try:
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Remove all existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Configure the root logger
        root_logger.setLevel(logging.DEBUG)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # Debug log file (Rotating by size)
        debug_handler = RotatingFileHandler(
            os.path.join(logs_dir, 'debug.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(detailed_formatter)
        
        # Error log file (Rotating daily)
        error_handler = TimedRotatingFileHandler(
            os.path.join(logs_dir, 'error.log'),
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days of error logs
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Trading log file (Rotating daily)
        trading_handler = TimedRotatingFileHandler(
            os.path.join(logs_dir, 'trading.log'),
            when='midnight',
            interval=1,
            backupCount=90,  # Keep 90 days of trading logs
            encoding='utf-8'
        )
        trading_handler.setLevel(logging.INFO)
        trading_handler.setFormatter(detailed_formatter)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to the logger
        root_logger.addHandler(debug_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(trading_handler)
        root_logger.addHandler(console_handler)
        
        # Set up exception logging
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                # Call the default handler for keyboard interrupt
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            root_logger.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Set the exception handler
        sys.excepthook = handle_exception
        
        # Log startup message
        root_logger.info("Logging system initialized")
        root_logger.debug(f"Log directory: {logs_dir}")
        
    except Exception as e:
        # If logging setup fails, at least try to print to console
        print(f"Error setting up logging: {str(e)}")
        traceback.print_exc()
        raise
