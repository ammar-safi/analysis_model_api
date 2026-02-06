from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.routers import sentiment, stance, health, cache
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
    description="API for analyzing sentiment and stance in English texts",
    version="1.0.0"
)

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

@app.get("/")
async def root():
    return {"message": "Sentiment and Stance Analysis API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)