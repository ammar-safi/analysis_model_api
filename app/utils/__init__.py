"""
Utility functions for the Sentiment and Stance Analysis API.
"""

from .helpers import (
    generate_request_id,
    get_current_timestamp,
    create_error_response_data,
    create_health_response_data
)

from .text_processor import TextProcessor

from .validators import (
    InputValidator,
    ValidationResult,
    validate_request_data,
    sanitize_text_input,
    extract_text_statistics,
    is_text_processable,
    normalize_confidence_score,
    create_validation_error_response
)

__all__ = [
    # Helper functions
    "generate_request_id",
    "get_current_timestamp", 
    "create_error_response_data",
    "create_health_response_data",
    
    # Text processing
    "TextProcessor",
    
    # Validation
    "InputValidator",
    "ValidationResult",
    "validate_request_data",
    "sanitize_text_input",
    "extract_text_statistics",
    "is_text_processable",
    "normalize_confidence_score",
    "create_validation_error_response"
]