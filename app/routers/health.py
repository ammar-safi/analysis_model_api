"""
Health Check Router
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import time
import logging

from app.models.responses import HealthResponse, ErrorResponse
from app.services.sentiment_service import SentimentService
from app.services.stance_service import StanceService
from app.exceptions import ProcessingError, ServiceUnavailableError
from app.utils.error_utils import generate_request_id

# Configure logging
logger = logging.getLogger(__name__)

# Store startup time for uptime calculation
startup_time = time.time()

# Create router
router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        503: {"model": ErrorResponse, "description": "Service Unavailable"}
    }
)

def get_sentiment_service() -> SentimentService:
    """Dependency to provide SentimentService instance"""
    return SentimentService()

def get_stance_service() -> StanceService:
    """Dependency to provide StanceService instance"""
    return StanceService()

def check_service_health(service_name: str, service_instance) -> str:
    """
    Check if a service is healthy by testing basic functionality
    
    Args:
        service_name: Name of the service
        service_instance: Instance of the service to test
        
    Returns:
        Health status: "healthy" or "unhealthy"
    """
    try:
        if service_name == "sentiment_service":
            # Test sentiment service with a simple text
            result = service_instance.analyze_sentiment("test")
            if result and hasattr(result, 'sentiment'):
                return "healthy"
        elif service_name == "stance_service":
            # Test stance service with a simple text and target
            result = service_instance.analyze_stance("test", "target")
            if result and hasattr(result, 'stance'):
                return "healthy"
        return "unhealthy"
    except Exception as e:
        logger.error(f"Health check failed for {service_name}: {str(e)}")
        return "unhealthy"

@router.get(
    "",
    response_model=HealthResponse,
    summary="System health check",
    description="Check the health status of the API and its services"
)
async def health_check(
    sentiment_service: SentimentService = Depends(get_sentiment_service),
    stance_service: StanceService = Depends(get_stance_service)
) -> HealthResponse:
    """
    Perform a comprehensive health check of the system.
    
    Returns system status, version information, uptime, and individual service health.
    """
    request_id = generate_request_id()
    timestamp = datetime.utcnow()
    uptime_seconds = time.time() - startup_time
    
    try:
        # Check individual services
        services_status = {
            "sentiment_service": check_service_health("sentiment_service", sentiment_service),
            "stance_service": check_service_health("stance_service", stance_service)
        }
        
        # Determine overall system health
        overall_status = "healthy" if all(status == "healthy" for status in services_status.values()) else "unhealthy"
        
        # Log health check
        logger.info(f"Health check {request_id} performed - Status: {overall_status}, Services: {services_status}")
        
        # If any critical services are unhealthy, raise an exception
        unhealthy_services = [name for name, status in services_status.items() if status == "unhealthy"]
        if unhealthy_services:
            logger.warning(f"Health check {request_id}: Unhealthy services detected: {unhealthy_services}")
            # Still return the response but with unhealthy status
        
        return HealthResponse(
            status=overall_status,
            version="1.0.0",
            timestamp=timestamp,
            services=services_status,
            uptime_seconds=uptime_seconds
        )
        
    except Exception as e:
        logger.error(f"Health check {request_id} failed: {str(e)}")
        raise ProcessingError(
            "Health check failed due to internal error",
            details={"request_id": request_id},
            original_error=e
        )