"""
Debug utilities for conditional logging.
"""
import os
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def is_debug_enabled() -> bool:
    """Check if debug logging is enabled.
    
    Returns:
        True if debug logging is enabled
    """
    return os.getenv("DEBUG_LOGGING", "false").lower() in ("true", "1", "yes", "on")


def debug_print(message: Any, flush: bool = True) -> None:
    """Print debug message only if debug logging is enabled.
    
    Args:
        message: Message to print
        flush: Whether to flush output immediately
    """
    if is_debug_enabled():
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] DEBUG: {message}", flush=flush)
        logger.debug(str(message))


def debug_log_request(endpoint: str, data: dict = None) -> None:
    """Log API request for debugging.
    
    Args:
        endpoint: API endpoint name
        data: Request data (optional)
    """
    if is_debug_enabled():
        message = f"API Request: {endpoint}"
        if data:
            message += f" - Data: {data}"
        debug_print(message)