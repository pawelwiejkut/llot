"""
Debug utilities for conditional logging
"""
import os

def is_debug_enabled():
    """Check if debug logging is enabled"""
    return os.getenv("DEBUG_LOGGING", "false").lower() in ("true", "1", "yes", "on")

def debug_print(message, flush=True):
    """Print debug message only if debug logging is enabled"""
    if is_debug_enabled():
        print(f"DEBUG: {message}", flush=flush)