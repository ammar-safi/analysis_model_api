"""
Custom exceptions for the Sentiment and Stance Analysis API.
"""

from typing import Optional, Dict, Any


class ProcessingError(Exception):
    """
    Exception raised when there's an error during text processing or analysis.
    
    This exception is used for internal processing errors that are not validation
    related but occur during the actual analysis operations.
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        self.message = message
        self.details = details or {}
        self.original_error = original_error
        super().__init__(self.message)


class ServiceUnavailableError(Exception):
    """
    Exception raised when a required service is unavailable.
    
    This exception is used when external dependencies or internal services
    are not available or fail to initialize properly.
    """
    
    def __init__(
        self, 
        service_name: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.service_name = service_name
        self.message = message
        self.details = details or {}
        super().__init__(f"Service '{service_name}' unavailable: {message}")


class TextValidationError(ValueError):
    """
    Exception raised when text validation fails.
    
    This is a specialized ValueError for text-specific validation issues.
    """
    
    def __init__(
        self, 
        message: str, 
        field: str = "text",
        details: Optional[Dict[str, Any]] = None
    ):
        self.field = field
        self.details = details or {}
        super().__init__(message)


class TargetValidationError(ValueError):
    """
    Exception raised when target entity validation fails.
    
    This is a specialized ValueError for target-specific validation issues.
    """
    
    def __init__(
        self, 
        message: str, 
        target: str = "",
        details: Optional[Dict[str, Any]] = None
    ):
        self.target = target
        self.details = details or {}
        super().__init__(message)