"""Logging configuration for drone simulator."""
import logging
import os
import sys
from pathlib import Path

def configure_logging(name=None, level=logging.INFO, log_file=None):
    """
    Configure logging for drone simulator components.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional file path for logging
    
    Returns:
        Configured logger
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    # Configure logger
    logger = logging.getLogger(name or __name__)
    logger.setLevel(level)
    
    # Clear existing handlers
    if logger.handlers:
        logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(component_name, log_to_file=True):
    """
    Get a logger for a specific component.
    
    Args:
        component_name: Name of the component
        log_to_file: Whether to log to a file
    
    Returns:
        Configured logger
    """
    # Create logs directory
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Set up logger
    log_file = None
    if log_to_file:
        log_file = logs_dir / f"{component_name}.log"
    
    return configure_logging(
        name=f"drone_simulator.{component_name}",
        level=logging.INFO,
        log_file=str(log_file) if log_file else None
    )