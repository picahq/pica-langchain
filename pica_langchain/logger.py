"""
Logging configuration for the Pica LangChain SDK.

This module provides a consistent logging interface for the entire SDK,
allowing for proper log level control and formatting suitable for enterprise use.
"""

import logging
import os
import sys
from typing import Optional, Union, Dict, Any

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

# Default format includes timestamp, level, and message
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logger = logging.getLogger("pica_langchain")

def configure_logging(
    level: Union[str, int] = "info",
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure the Pica LangChain logger.
    
    Args:
        level: The log level to use. Can be a string ('debug', 'info', 'warning', 'error', 'critical') or a logging level constant.
        format_string: Custom format string for log messages. If None, uses the default format.
        log_file: Optional file path to write logs to. If None, logs are only written to stderr.
    """
    # Convert string level to logging constant if needed
    if isinstance(level, str):
        level = level.lower()
        if level not in LOG_LEVELS:
            valid_levels = ", ".join(LOG_LEVELS.keys())
            print(f"Invalid log level: {level}. Valid levels are: {valid_levels}")
            level = "info"
        level = LOG_LEVELS[level]
    
    # Clear any existing handlers
    logger.handlers = []
    
    logger.setLevel(level)
    
    formatter = logging.Formatter(format_string or DEFAULT_FORMAT)
    
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file is specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to create log file handler: {e}")
    
    # To avoid duplicate logs
    logger.propagate = False


log_level = os.environ.get("PICA_LOG_LEVEL", "info").lower()
log_file = os.environ.get("PICA_LOG_FILE")

configure_logging(level=log_level, log_file=log_file)

def get_logger() -> logging.Logger:
    """
    Get the Pica LangChain logger.
    
    Returns:
        The configured logger instance.
    """
    return logger

def log_request_response(
    method: str,
    url: str,
    request_data: Optional[Dict[str, Any]] = None,
    response_status: Optional[Any] = None,
    response_data: Optional[Any] = None,
    error: Optional[Exception] = None,
) -> None:
    """
    Log API request and response details at the appropriate level.
    
    Args:
        method: HTTP method used (GET, POST, etc.)
        url: The URL of the request
        request_data: Optional request data/parameters
        response_status: Optional HTTP status code
        response_data: Optional response data
        error: Optional exception if the request failed
    """
    # Mask pica secret in headers
    if request_data and isinstance(request_data, dict):
        safe_request_data = request_data.copy()
        
        if "headers" in safe_request_data and isinstance(safe_request_data["headers"], dict):
            if "x-pica-secret" in safe_request_data["headers"]:
                safe_request_data["headers"]["x-pica-secret"] = "********"
    else:
        safe_request_data = request_data
    
    if error:
        logger.error(
            f"API Request Failed: {method} {url}",
            extra={
                "method": method,
                "url": url,
                "request_data": safe_request_data,
                "error": str(error)
            }
        )
    elif response_status:
        # Check if response_status is a mock or a real status code
        try:
            is_error = int(response_status) >= 400
        except (ValueError, TypeError):
            is_error = False
            
        if is_error:
            log_func = logger.warning if int(response_status) < 500 else logger.error
            log_func(
                f"API Response Error: {method} {url} - Status: {response_status}",
                extra={
                    "method": method,
                    "url": url,
                    "request_data": safe_request_data,
                    "status": response_status,
                    "response": response_data
                }
            )
        else:
            logger.debug(
                f"API Response Success: {method} {url} - Status: {response_status}",
                extra={
                    "method": method,
                    "url": url,
                    "request_data": safe_request_data,
                    "status": response_status,
                    "response": response_data
                }
            )
    else:
        logger.debug(
            f"API Request: {method} {url}",
            extra={
                "method": method,
                "url": url,
                "request_data": safe_request_data
            }
        )
