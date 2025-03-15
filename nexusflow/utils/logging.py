"""
Logging utilities for NexusFlow.ai

This module provides customized logging setup and utilities for the NexusFlow system.
"""

import logging
import os
import sys
import json
from typing import Dict, Any, Optional, Union
from datetime import datetime
import logging.handlers

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    console_output: bool = True,
    json_format: bool = False,
    log_dir: str = "logs"
) -> None:
    """
    Set up logging with a standard format and optional file output
    
    Args:
        level: Logging level
        log_file: Path to log file (None for no file logging)
        log_format: Custom log format string
        date_format: Custom date format string
        console_output: Whether to output logs to console
        json_format: Whether to format logs as JSON
        log_dir: Directory for log files when using rotating or daily file handlers
    """
    # Create loggers
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Default formats
    if log_format is None:
        if json_format:
            log_format = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
        else:
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if date_format is None:
        date_format = '%Y-%m-%d %H:%M:%S'
    
    # Create formatter
    formatter = logging.Formatter(log_format, date_format)
    
    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        if log_file.lower() == 'auto':
            # Use a rotating file handler
            os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                os.path.join(log_dir, 'nexusflow.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        elif log_file.lower() == 'daily':
            # Use a timed rotating file handler
            os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.handlers.TimedRotatingFileHandler(
                os.path.join(log_dir, 'nexusflow.log'),
                when='midnight',
                backupCount=30
            )
        else:
            # Use a regular file handler with the specified file
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
        
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Log initial message
    root_logger.info(f"Logging initialized at level {logging.getLevelName(level)}")

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger with the given name
    
    Args:
        name: Logger name
        level: Optional specific level for this logger
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings
    """
    def __init__(self, fmt=None, datefmt=None, style='%', **kwargs):
        """Initialize the formatter"""
        super().__init__(fmt, datefmt, style, **kwargs)
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON"""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra attributes
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", "filename",
                          "funcName", "id", "levelname", "levelno", "lineno", "module",
                          "msecs", "message", "msg", "name", "pathname", "process",
                          "processName", "relativeCreated", "stack_info", "thread", "threadName"]:
                log_data[key] = value
        
        return json.dumps(log_data)

class StructuredLogAdapter(logging.LoggerAdapter):
    """
    Adapter to add structured data to log messages
    """
    def process(self, msg, kwargs):
        """Process the logging message and keyword arguments"""
        # If kwargs contains 'extra', update it with self.extra
        if 'extra' not in kwargs:
            kwargs['extra'] = self.extra
        else:
            kwargs['extra'].update(self.extra)
        return msg, kwargs

def get_structured_logger(name: str, **extra) -> StructuredLogAdapter:
    """
    Get a logger that supports structured logging with additional context
    
    Args:
        name: Logger name
        **extra: Additional context to include in all log messages
        
    Returns:
        Structured logger adapter
    """
    logger = logging.getLogger(name)
    return StructuredLogAdapter(logger, extra)
