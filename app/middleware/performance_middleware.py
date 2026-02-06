"""
Performance Monitoring Middleware for FastAPI
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.performance_monitor import get_performance_monitor
from app.utils.error_utils import generate_request_id

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically track request performance metrics
    """
    
    def __init__(self, app, exclude_paths: list = None):
        """
        Initialize performance middleware
        
        Args:
            app: FastAPI application instance
            exclude_paths: List of paths to exclude from monitoring (e.g., ["/health", "/docs"])
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/favicon.ico"]
        self.performance_monitor = get_performance_monitor()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track performance metrics
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Skip monitoring for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Generate request ID if not present
        request_id = getattr(request.state, 'request_id', None)
        if not request_id:
            request_id = generate_request_id()
            request.state.request_id = request_id
        
        # Extract endpoint information
        endpoint = request.url.path
        method = request.method
        
        # Start performance tracking
        metrics = self.performance_monitor.start_request(request_id, endpoint, method)
        
        # Track cache hit status (will be updated by services)
        cache_hit = False
        error_message = None
        
        try:
            # Process request
            response = await call_next(request)
            
            # Check if cache was used (services should set this in request state)
            cache_hit = getattr(request.state, 'cache_hit', False)
            
            # Complete performance tracking
            self.performance_monitor.complete_request(
                request_id=request_id,
                status_code=response.status_code,
                cache_hit=cache_hit
            )
            
            # Add performance headers to response
            if metrics.duration_ms:
                response.headers["X-Response-Time"] = f"{metrics.duration_ms:.2f}ms"
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Cache-Hit"] = "true" if cache_hit else "false"
            
            return response
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Request {request_id} failed: {error_message}")
            
            # Complete tracking with error
            self.performance_monitor.complete_request(
                request_id=request_id,
                status_code=500,
                cache_hit=cache_hit,
                error=error_message
            )
            
            # Re-raise the exception
            raise


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for detailed request/response logging
    """
    
    def __init__(self, app, log_level: str = "INFO"):
        """
        Initialize request logging middleware
        
        Args:
            app: FastAPI application instance
            log_level: Logging level for requests
        """
        super().__init__(app)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = logging.getLogger("request_logger")
        self.logger.setLevel(self.log_level)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Log request and response details
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        start_time = time.time()
        
        # Get request ID
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Log request details
        self.logger.log(
            self.log_level,
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response details
            self.logger.log(
                self.log_level,
                f"Response {request_id}: {response.status_code} "
                f"in {duration_ms:.2f}ms"
            )
            
            return response
            
        except Exception as e:
            # Calculate response time for failed requests
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            self.logger.error(
                f"Request {request_id} failed after {duration_ms:.2f}ms: {str(e)}"
            )
            
            # Re-raise the exception
            raise


class MemoryMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for monitoring memory usage during requests
    """
    
    def __init__(self, app, memory_threshold_mb: float = 500.0):
        """
        Initialize memory monitoring middleware
        
        Args:
            app: FastAPI application instance
            memory_threshold_mb: Memory usage threshold for warnings (MB)
        """
        super().__init__(app)
        self.memory_threshold_mb = memory_threshold_mb
        self.logger = logging.getLogger("memory_monitor")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Monitor memory usage during request processing
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        try:
            import psutil
            process = psutil.Process()
            
            # Get memory usage before request
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process request
            response = await call_next(request)
            
            # Get memory usage after request
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_delta = memory_after - memory_before
            
            # Log memory usage if significant change or high usage
            request_id = getattr(request.state, 'request_id', 'unknown')
            
            if memory_after > self.memory_threshold_mb:
                self.logger.warning(
                    f"High memory usage for request {request_id}: "
                    f"{memory_after:.2f}MB (delta: {memory_delta:+.2f}MB)"
                )
            elif abs(memory_delta) > 10:  # Log if memory change > 10MB
                self.logger.info(
                    f"Memory change for request {request_id}: "
                    f"{memory_delta:+.2f}MB (total: {memory_after:.2f}MB)"
                )
            
            # Add memory info to response headers (for debugging)
            response.headers["X-Memory-Usage"] = f"{memory_after:.2f}MB"
            response.headers["X-Memory-Delta"] = f"{memory_delta:+.2f}MB"
            
            return response
            
        except ImportError:
            # psutil not available, skip memory monitoring
            self.logger.warning("psutil not available, skipping memory monitoring")
            return await call_next(request)
        
        except Exception as e:
            # Don't fail requests due to monitoring errors
            self.logger.error(f"Memory monitoring error: {e}")
            return await call_next(request)