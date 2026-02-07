"""
Stance Analysis Router
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import logging

from app.models.requests import StanceRequest
from app.models.responses import StanceResponse, ErrorResponse
from app.services.stance_service import StanceService
from app.exceptions import ProcessingError, TextValidationError, TargetValidationError
from app.utils.error_utils import generate_request_id

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/stance-analysis",
    tags=["stance"],
    responses={
        400: {"model": ErrorResponse, "description": "Validation Error"},
        422: {"model": ErrorResponse, "description": "Processing Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)

# Dependency to get stance service
def get_stance_service() -> StanceService:
    """Dependency to provide StanceService instance"""
    return StanceService()

@router.post(
    "",
    response_model=StanceResponse,
    summary="Analyze stance towards target",
    description="Analyze the stance of English text towards a specific target entity"
)
async def analyze_stance(
    request: StanceRequest,
    stance_service: StanceService = Depends(get_stance_service)
) -> StanceResponse:
    """
    Analyze stance of the provided text towards a target entity.
    
    - **text**: The English text to analyze (1-5000 characters)
    - **target**: The target entity to analyze stance towards (1-200 characters)
    
    Returns stance classification (supportive, opposing, neutral) with confidence score.
    """
    request_id = generate_request_id()
    timestamp = datetime.utcnow()
    
    try:
        logger.info(f"Processing stance analysis request {request_id} for target: {request.target}")
        
        # Additional text validation
        if not request.text.strip():
            raise TextValidationError(
                "Text cannot be empty or contain only whitespace",
                field="text",
                details={"provided_length": len(request.text)}
            )
        
        # Validate target is not empty after stripping
        if not request.target.strip():
            raise TargetValidationError(
                "Target entity cannot be empty or contain only whitespace",
                target=request.target,
                details={"provided_length": len(request.target)}
            )
        
        # Analyze stance
        result = stance_service.analyze_stance(request.text, request.target)
        
        # Log warning if fallback was used
        if result.fallback_used and result.warning:
            logger.warning(f"Request {request_id}: {result.warning}")
        
        # Create response
        response = StanceResponse(
            stance=result.stance,
            confidence=result.confidence,
            target=request.target,
            request_id=request_id,
            timestamp=timestamp
        )
        
        logger.info(f"Request {request_id} completed successfully: {result.stance} towards '{request.target}' ({result.confidence:.3f})")
        return response
        
    except (TextValidationError, TargetValidationError):
        # Re-raise custom validation errors to be handled by exception handlers
        raise
        
    except ValueError as e:
        # Convert ValueError to appropriate validation error
        error_msg = str(e).lower()
        if "target" in error_msg:
            logger.error(f"Target validation error for request {request_id}: {str(e)}")
            raise TargetValidationError(
                str(e),
                target=request.target,
                details={"request_id": request_id}
            )
        else:
            logger.error(f"Text validation error for request {request_id}: {str(e)}")
            raise TextValidationError(
                str(e),
                field="text",
                details={"request_id": request_id}
            )
    
    except Exception as e:
        # Convert general exceptions to ProcessingError
        logger.error(f"Processing error for request {request_id}: {str(e)}")
        raise ProcessingError(
            "Failed to analyze stance. Please try again.",
            details={"request_id": request_id, "target": request.target},
            original_error=e
        )