"""
Utility functions for the Sentiment and Stance Analysis API.
"""

import uuid
import time
from datetime import datetime
from typing import Optional


def generate_request_id(prefix: str = "req") -> str:
    """
    Generate a unique request ID.
    
    Args:
        prefix: Optional prefix for the request ID
        
    Returns:
        A unique request ID string
    """
    timestamp = int(time.time() * 1000)  # milliseconds
    unique_id = str(uuid.uuid4())[:8]  # first 8 characters of UUID
    return f"{prefix}_{timestamp}_{unique_id}"


def get_current_timestamp() -> datetime:
    """
    Get the current UTC timestamp.
    
    Returns:
        Current datetime in UTC
    """
    return datetime.utcnow()


def create_error_response_data(
    error_type: str,
    message: str,
    details: Optional[dict] = None,
    request_id: Optional[str] = None
) -> dict:
    """
    Create standardized error response data.
    
    Args:
        error_type: Type or category of the error
        message: Human-readable error message
        details: Additional error details
        request_id: Request ID, will be generated if not provided
        
    Returns:
        Dictionary containing error response data
    """
    return {
        "error": error_type,
        "message": message,
        "details": details or {},
        "request_id": request_id or generate_request_id("err"),
        "timestamp": get_current_timestamp()
    }


def create_health_response_data(
    status: str = "healthy",
    version: str = "1.0.0",
    services: Optional[dict] = None,
    uptime_seconds: Optional[float] = None
) -> dict:
    """
    Create standardized health response data.
    
    Args:
        status: Overall system health status
        version: API version
        services: Status of individual services
        uptime_seconds: System uptime in seconds
        
    Returns:
        Dictionary containing health response data
    """
    return {
        "status": status,
        "version": version,
        "timestamp": get_current_timestamp(),
        "services": services or {
            "sentiment_service": "healthy",
            "stance_service": "healthy"
        },
        "uptime_seconds": uptime_seconds or 0.0
    }