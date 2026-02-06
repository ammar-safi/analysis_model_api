"""
Exception handlers for the Sentiment and Stance Analysis API.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from datetime import datetime
import logging
import uuid
from typing import Union

from app.exceptions import (
    ProcessingError, 
    ServiceUnavailableError, 
    TextValidationError, 
    TargetValidationError
)

# Configure logging
logger = logging.getLogger(__name__)


def generate_request_id() -> str:
    """Generate unique request ID for error responses"""
    return f"err_{uuid.uuid4().hex[:12]}"


async def validation_exception_handler(
    request: Request, 
    exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    This handler catches validation errors from request models and returns
    a standardized error response with detailed validation information.
    """
    request_id = generate_request_id()
    timestamp = datetime.utcnow()
    
    # Extract validation error details
    error_details = []
    for error in exc.errors():
        error_detail = {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        if "input" in error:
            error_detail["input"] = str(error["input"])[:100]  # Limit input length
        error_details.append(error_detail)
    
    logger.warning(f"Validation error {request_id}: {len(error_details)} validation issues")
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": {
                "validation_errors": error_details,
                "error_count": len(error_details)
            },
            "request_id": request_id,
            "timestamp": timestamp.isoformat()
        }
    )


async def text_validation_exception_handler(
    request: Request, 
    exc: TextValidationError
) -> JSONResponse:
    """
    Handle custom text validation errors.
    
    This handler catches text-specific validation errors and returns
    a standardized error response.
    """
    request_id = generate_request_id()
    timestamp = datetime.utcnow()
    
    logger.warning(f"Text validation error {request_id}: {exc}")
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "TextValidationError",
            "message": str(exc),
            "details": {
                "field": exc.field,
                **exc.details
            },
            "request_id": request_id,
            "timestamp": timestamp.isoformat()
        }
    )


async def target_validation_exception_handler(
    request: Request, 
    exc: TargetValidationError
) -> JSONResponse:
    """
    Handle custom target validation errors.
    
    This handler catches target-specific validation errors and returns
    a standardized error response.
    """
    request_id = generate_request_id()
    timestamp = datetime.utcnow()
    
    logger.warning(f"Target validation error {request_id}: {exc}")
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "TargetValidationError",
            "message": str(exc),
            "details": {
                "target": exc.target,
                **exc.details
            },
            "request_id": request_id,
            "timestamp": timestamp.isoformat()
        }
    )


async def processing_exception_handler(
    request: Request, 
    exc: ProcessingError
) -> JSONResponse:
    """
    Handle processing errors during analysis.
    
    This handler catches errors that occur during text processing or analysis
    and returns a standardized error response.
    """
    request_id = generate_request_id()
    timestamp = datetime.utcnow()
    
    logger.error(f"Processing error {request_id}: {exc.message}")
    if exc.original_error:
        logger.error(f"Original error: {exc.original_error}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "ProcessingError",
            "message": exc.message,
            "details": exc.details,
            "request_id": request_id,
            "timestamp": timestamp.isoformat()
        }
    )


async def service_unavailable_exception_handler(
    request: Request, 
    exc: ServiceUnavailableError
) -> JSONResponse:
    """
    Handle service unavailable errors.
    
    This handler catches errors when required services are unavailable
    and returns a standardized error response.
    """
    request_id = generate_request_id()
    timestamp = datetime.utcnow()
    
    logger.error(f"Service unavailable error {request_id}: {exc.service_name} - {exc.message}")
    
    return JSONResponse(
        status_code=503,
        content={
            "error": "ServiceUnavailableError",
            "message": f"Service '{exc.service_name}' is currently unavailable",
            "details": {
                "service": exc.service_name,
                "reason": exc.message,
                **exc.details
            },
            "request_id": request_id,
            "timestamp": timestamp.isoformat()
        }
    )


async def http_exception_handler(
    request: Request, 
    exc: HTTPException
) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions.
    
    This handler catches HTTPException instances and ensures they follow
    our standardized error response format.
    """
    request_id = generate_request_id()
    timestamp = datetime.utcnow()
    
    # If detail is already a dict (from our routers), use it
    if isinstance(exc.detail, dict):
        content = exc.detail
        # Ensure request_id and timestamp are present
        if "request_id" not in content:
            content["request_id"] = request_id
        if "timestamp" not in content:
            content["timestamp"] = timestamp.isoformat()
    else:
        # Create standardized response for string details
        content = {
            "error": "HTTPException",
            "message": str(exc.detail),
            "details": {},
            "request_id": request_id,
            "timestamp": timestamp.isoformat()
        }
    
    logger.warning(f"HTTP exception {request_id}: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


async def generic_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    """
    Handle any unhandled exceptions.
    
    This is the catch-all handler for any exceptions that aren't handled
    by more specific handlers. It logs the error and returns a generic
    internal server error response.
    """
    request_id = generate_request_id()
    timestamp = datetime.utcnow()
    
    logger.error(f"Unhandled exception {request_id}: {type(exc).__name__}: {exc}")
    logger.exception("Full exception traceback:")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An internal server error occurred. Please try again later.",
            "details": {
                "error_type": type(exc).__name__
            },
            "request_id": request_id,
            "timestamp": timestamp.isoformat()
        }
    )