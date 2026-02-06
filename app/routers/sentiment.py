"""
Sentiment Analysis Router
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import logging

from app.models.requests import SentimentRequest
from app.models.responses import SentimentResponse, ErrorResponse
from app.services.sentiment_service import SentimentService
from app.exceptions import ProcessingError, TextValidationError
from app.utils.error_utils import generate_request_id

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/sentiment-analysis",
    tags=["sentiment"],
    responses={
        400: {"model": ErrorResponse, "description": "Validation Error"},
        422: {"model": ErrorResponse, "description": "Processing Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)

# Dependency to get sentiment service
def get_sentiment_service() -> SentimentService:
    """Dependency to provide SentimentService instance"""
    return SentimentService()

@router.post(
    "",
    response_model=SentimentResponse,
    summary="Analyze text sentiment",
    description="Analyze the sentiment of English text and return classification with confidence score"
)
async def analyze_sentiment(
    request: SentimentRequest,
    sentiment_service: SentimentService = Depends(get_sentiment_service)
) -> SentimentResponse:
    """
    Analyze sentiment of the provided text.
    
    - **text**: The English text to analyze (1-5000 characters)
    
    Returns sentiment classification (positive, negative, normal) with confidence score.
    """
    request_id = generate_request_id()
    timestamp = datetime.utcnow()
    
    try:
        logger.info(f"Processing sentiment analysis request {request_id}")
        
        # Additional text validation
        if not request.text.strip():
            raise TextValidationError(
                "Text cannot be empty or contain only whitespace",
                field="text",
                details={"provided_length": len(request.text)}
            )
        
        # Analyze sentiment
        result = sentiment_service.analyze_sentiment(request.text)
        
        # Log warning if fallback was used
        if result.fallback_used and result.warning:
            logger.warning(f"Request {request_id}: {result.warning}")
        
        # Create response
        response = SentimentResponse(
            sentiment=result.sentiment,
            confidence=result.confidence,
            request_id=request_id,
            timestamp=timestamp
        )
        
        logger.info(f"Request {request_id} completed successfully: {result.sentiment} ({result.confidence:.3f})")
        return response
        
    except TextValidationError:
        # Re-raise custom validation errors to be handled by exception handlers
        raise
        
    except ValueError as e:
        # Convert ValueError to TextValidationError for consistent handling
        logger.error(f"Validation error for request {request_id}: {str(e)}")
        raise TextValidationError(
            str(e),
            field="text",
            details={"request_id": request_id}
        )
    
    except Exception as e:
        # Convert general exceptions to ProcessingError
        logger.error(f"Processing error for request {request_id}: {str(e)}")
        raise ProcessingError(
            "Failed to analyze sentiment. Please try again.",
            details={"request_id": request_id},
            original_error=e
        )