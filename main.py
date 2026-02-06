from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.routers import sentiment, stance, health, cache, metrics
from app.middleware import PerformanceMiddleware, RequestLoggingMiddleware, MemoryMonitoringMiddleware
from app.exception_handlers import (
    validation_exception_handler,
    text_validation_exception_handler,
    target_validation_exception_handler,
    processing_exception_handler,
    service_unavailable_exception_handler,
    http_exception_handler,
    generic_exception_handler
)
from app.exceptions import (
    ProcessingError,
    ServiceUnavailableError,
    TextValidationError,
    TargetValidationError
)

app = FastAPI(
    title="Sentiment and Stance Analysis API",
    description="""
    ## High-Performance Text Analysis API
    
    This API provides advanced sentiment and stance analysis for English texts using state-of-the-art NLP techniques.
    
    ### Features
    
    * **Sentiment Analysis**: Classify text as positive, negative, or neutral with confidence scores
    * **Stance Analysis**: Determine stance towards specific targets (supportive, opposing, neutral)
    * **High Performance**: Built-in caching and performance monitoring
    * **Real-time Metrics**: Comprehensive performance and system monitoring
    * **Robust Error Handling**: Detailed error messages and validation
    
    ### Performance
    
    * Response times: 50-300ms (cached: <10ms)
    * Concurrent requests: 100+ req/sec
    * Cache hit rate: 60-80% typical
    
    ### Monitoring
    
    * Performance metrics at `/metrics/performance`
    * Cache statistics at `/metrics/cache`
    * System monitoring at `/metrics/system`
    * Health checks at `/health`
    
    ### Quick Start
    
    1. **Sentiment Analysis**:
       ```bash
       curl -X POST "/sentiment-analysis" \\
            -H "Content-Type: application/json" \\
            -d '{"text": "I love this product!"}'
       ```
    
    2. **Stance Analysis**:
       ```bash
       curl -X POST "/stance-analysis" \\
            -H "Content-Type: application/json" \\
            -d '{"text": "Apple makes great phones", "target": "Apple"}'
       ```
    
    ### Support
    
    * Interactive documentation: `/docs`
    * Alternative docs: `/redoc`
    * Health status: `/health`
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.example.com",
            "description": "Production server"
        }
    ]
)

# Add performance monitoring middleware
app.add_middleware(PerformanceMiddleware, exclude_paths=["/docs", "/redoc", "/openapi.json", "/favicon.ico", "/metrics"])
app.add_middleware(RequestLoggingMiddleware, log_level="INFO")
app.add_middleware(MemoryMonitoringMiddleware, memory_threshold_mb=500.0)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(TextValidationError, text_validation_exception_handler)
app.add_exception_handler(TargetValidationError, target_validation_exception_handler)
app.add_exception_handler(ProcessingError, processing_exception_handler)
app.add_exception_handler(ServiceUnavailableError, service_unavailable_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
app.include_router(sentiment.router)
app.include_router(stance.router)
app.include_router(health.router)
app.include_router(cache.router)
app.include_router(metrics.router)

@app.get("/")
async def root():
    return {"message": "Sentiment and Stance Analysis API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)