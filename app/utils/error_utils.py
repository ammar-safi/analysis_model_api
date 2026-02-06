"""
Error handling utilities for consistent error responses.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional


def generate_request_id() -> str:
    """Generate unique request ID"""
    return f"req_{uuid.uuid4().hex[:12]}"


def create_error_response(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.
    
    Args:
        error_type: The type/category of error
        message: Human-readable error message
        details: Additional error details
        request_id: Unique request identifier
        
    Returns:
        Standardized error response dictionary
    """
    if request_id is None:
        request_id = generate_request_id()
    
    return {
        "error": error_type,
        "message": message,
        "details": details or {},
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat()
    }


# Standard HTTP status codes for different error types
ERROR_STATUS_CODES = {
    "ValidationError": 400,
    "TextValidationError": 400,
    "TargetValidationError": 400,
    "ProcessingError": 422,
    "ServiceUnavailableError": 503,
    "InternalServerError": 500,
    "NotFoundError": 404,
    "MethodNotAllowedError": 405,
    "TimeoutError": 408,
    "RateLimitError": 429
}


def get_status_code_for_error(error_type: str) -> int:
    """
    Get the appropriate HTTP status code for an error type.
    
    Args:
        error_type: The error type/category
        
    Returns:
        HTTP status code
    """
    return ERROR_STATUS_CODES.get(error_type, 500)


# Standard error messages for common scenarios
STANDARD_ERROR_MESSAGES = {
    "text_empty": "Text cannot be empty",
    "text_too_long": "Text exceeds maximum length limit",
    "text_too_short": "Text is too short for reliable analysis",
    "text_invalid_language": "Text must be in English",
    "target_empty": "Target entity cannot be empty",
    "target_too_long": "Target entity exceeds maximum length limit",
    "processing_failed": "Failed to process the request. Please try again.",
    "service_unavailable": "Service is temporarily unavailable. Please try again later.",
    "internal_error": "An internal server error occurred. Please try again later.",
    "invalid_request": "The request format is invalid",
    "missing_required_field": "Required field is missing"
}


def get_standard_message(message_key: str, **kwargs) -> str:
    """
    Get a standard error message, optionally formatted with parameters.
    
    Args:
        message_key: Key for the standard message
        **kwargs: Parameters to format the message with
        
    Returns:
        Formatted error message
    """
    message = STANDARD_ERROR_MESSAGES.get(message_key, "An error occurred")
    try:
        return message.format(**kwargs)
    except (KeyError, ValueError):
        return message