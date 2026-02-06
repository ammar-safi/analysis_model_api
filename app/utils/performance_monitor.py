"""
Performance Monitoring and Metrics Collection
"""
import time
import psutil
import logging
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from functools import wraps
from contextlib import contextmanager
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    request_id: str
    endpoint: str
    method: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    status_code: Optional[int] = None
    memory_before_mb: Optional[float] = None
    memory_after_mb: Optional[float] = None
    memory_delta_mb: Optional[float] = None
    cache_hit: bool = False
    error: Optional[str] = None
    
    def complete(self, status_code: int, memory_after_mb: float, cache_hit: bool = False, error: Optional[str] = None):
        """Mark request as completed and calculate metrics"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status_code = status_code
        self.memory_after_mb = memory_after_mb
        if self.memory_before_mb:
            self.memory_delta_mb = memory_after_mb - self.memory_before_mb
        self.cache_hit = cache_hit
        self.error = error


@dataclass
class PerformanceStats:
    """Aggregated performance statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Response time statistics
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = float('inf')
    max_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    
    # Memory statistics
    avg_memory_usage_mb: float = 0.0
    peak_memory_usage_mb: float = 0.0
    avg_memory_delta_mb: float = 0.0
    
    # Endpoint statistics
    endpoint_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Time window
    window_start: datetime = field(default_factory=datetime.utcnow)
    window_end: Optional[datetime] = None


class PerformanceMonitor:
    """
    Performance monitoring system for tracking request metrics,
    response times, memory usage, and system performance
    """
    
    def __init__(self, max_history: int = 10000, stats_window_minutes: int = 60):
        """
        Initialize performance monitor
        
        Args:
            max_history: Maximum number of request metrics to keep in memory
            stats_window_minutes: Time window for calculating statistics (minutes)
        """
        self.max_history = max_history
        self.stats_window = timedelta(minutes=stats_window_minutes)
        
        # Thread-safe storage
        self._lock = threading.RLock()
        self._request_history: List[RequestMetrics] = []
        self._active_requests: Dict[str, RequestMetrics] = {}
        
        # System monitoring
        self._system_stats = {
            'cpu_percent': 0.0,
            'memory_percent': 0.0,
            'memory_available_mb': 0.0,
            'disk_usage_percent': 0.0,
            'last_updated': time.time()
        }
        
        # Start background monitoring
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self._monitor_thread.start()
    
    def start_request(self, request_id: str, endpoint: str, method: str = "POST") -> RequestMetrics:
        """
        Start tracking a new request
        
        Args:
            request_id: Unique request identifier
            endpoint: API endpoint being called
            method: HTTP method
            
        Returns:
            RequestMetrics object for this request
        """
        with self._lock:
            # Get current memory usage
            memory_mb = self._get_memory_usage_mb()
            
            metrics = RequestMetrics(
                request_id=request_id,
                endpoint=endpoint,
                method=method,
                start_time=time.time(),
                memory_before_mb=memory_mb
            )
            
            self._active_requests[request_id] = metrics
            logger.debug(f"Started tracking request {request_id} to {endpoint}")
            
            return metrics
    
    def complete_request(self, request_id: str, status_code: int, cache_hit: bool = False, error: Optional[str] = None):
        """
        Mark a request as completed and record final metrics
        
        Args:
            request_id: Request identifier
            status_code: HTTP status code
            cache_hit: Whether the request was served from cache
            error: Error message if request failed
        """
        with self._lock:
            if request_id not in self._active_requests:
                logger.warning(f"Attempted to complete unknown request: {request_id}")
                return
            
            metrics = self._active_requests.pop(request_id)
            memory_mb = self._get_memory_usage_mb()
            
            metrics.complete(status_code, memory_mb, cache_hit, error)
            
            # Add to history
            self._request_history.append(metrics)
            
            # Trim history if needed
            if len(self._request_history) > self.max_history:
                self._request_history = self._request_history[-self.max_history:]
            
            logger.debug(f"Completed request {request_id}: {metrics.duration_ms:.2f}ms, status {status_code}")
    
    def get_current_stats(self) -> PerformanceStats:
        """
        Get current performance statistics for the configured time window
        
        Returns:
            PerformanceStats object with aggregated metrics
        """
        with self._lock:
            cutoff_time = datetime.utcnow() - self.stats_window
            
            # Filter recent requests
            recent_requests = [
                req for req in self._request_history
                if req.end_time and datetime.fromtimestamp(req.end_time) > cutoff_time
            ]
            
            if not recent_requests:
                return PerformanceStats()
            
            # Calculate basic stats
            total_requests = len(recent_requests)
            successful_requests = len([r for r in recent_requests if r.status_code and r.status_code < 400])
            failed_requests = total_requests - successful_requests
            cache_hits = len([r for r in recent_requests if r.cache_hit])
            cache_misses = total_requests - cache_hits
            
            # Response time statistics
            response_times = [r.duration_ms for r in recent_requests if r.duration_ms is not None]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
            min_response_time = min(response_times) if response_times else 0.0
            max_response_time = max(response_times) if response_times else 0.0
            
            # Calculate percentiles
            sorted_times = sorted(response_times)
            p95_index = int(len(sorted_times) * 0.95)
            p99_index = int(len(sorted_times) * 0.99)
            p95_response_time = sorted_times[p95_index] if sorted_times else 0.0
            p99_response_time = sorted_times[p99_index] if sorted_times else 0.0
            
            # Memory statistics
            memory_usages = [r.memory_after_mb for r in recent_requests if r.memory_after_mb is not None]
            memory_deltas = [r.memory_delta_mb for r in recent_requests if r.memory_delta_mb is not None]
            
            avg_memory_usage = sum(memory_usages) / len(memory_usages) if memory_usages else 0.0
            peak_memory_usage = max(memory_usages) if memory_usages else 0.0
            avg_memory_delta = sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0.0
            
            # Endpoint statistics
            endpoint_stats = {}
            for endpoint in set(r.endpoint for r in recent_requests):
                endpoint_requests = [r for r in recent_requests if r.endpoint == endpoint]
                endpoint_times = [r.duration_ms for r in endpoint_requests if r.duration_ms is not None]
                endpoint_successes = len([r for r in endpoint_requests if r.status_code and r.status_code < 400])
                
                endpoint_stats[endpoint] = {
                    'total_requests': len(endpoint_requests),
                    'successful_requests': endpoint_successes,
                    'failed_requests': len(endpoint_requests) - endpoint_successes,
                    'avg_response_time_ms': sum(endpoint_times) / len(endpoint_times) if endpoint_times else 0.0,
                    'cache_hits': len([r for r in endpoint_requests if r.cache_hit])
                }
            
            return PerformanceStats(
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                avg_response_time_ms=avg_response_time,
                min_response_time_ms=min_response_time,
                max_response_time_ms=max_response_time,
                p95_response_time_ms=p95_response_time,
                p99_response_time_ms=p99_response_time,
                avg_memory_usage_mb=avg_memory_usage,
                peak_memory_usage_mb=peak_memory_usage,
                avg_memory_delta_mb=avg_memory_delta,
                endpoint_stats=endpoint_stats,
                window_start=cutoff_time,
                window_end=datetime.utcnow()
            )
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get current system performance statistics
        
        Returns:
            Dictionary with system metrics
        """
        with self._lock:
            return self._system_stats.copy()
    
    def get_detailed_metrics(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get detailed metrics including recent request history
        
        Args:
            limit: Maximum number of recent requests to include
            
        Returns:
            Dictionary with detailed performance metrics
        """
        with self._lock:
            stats = self.get_current_stats()
            system_stats = self.get_system_stats()
            
            # Get recent requests
            recent_requests = self._request_history[-limit:] if self._request_history else []
            request_data = []
            
            for req in recent_requests:
                request_data.append({
                    'request_id': req.request_id,
                    'endpoint': req.endpoint,
                    'method': req.method,
                    'duration_ms': req.duration_ms,
                    'status_code': req.status_code,
                    'memory_delta_mb': req.memory_delta_mb,
                    'cache_hit': req.cache_hit,
                    'timestamp': datetime.fromtimestamp(req.start_time).isoformat() if req.start_time else None,
                    'error': req.error
                })
            
            return {
                'performance_stats': {
                    'total_requests': stats.total_requests,
                    'successful_requests': stats.successful_requests,
                    'failed_requests': stats.failed_requests,
                    'success_rate_percent': round((stats.successful_requests / stats.total_requests * 100) if stats.total_requests > 0 else 0, 2),
                    'cache_hits': stats.cache_hits,
                    'cache_misses': stats.cache_misses,
                    'cache_hit_rate_percent': round((stats.cache_hits / stats.total_requests * 100) if stats.total_requests > 0 else 0, 2),
                    'avg_response_time_ms': round(stats.avg_response_time_ms, 2),
                    'min_response_time_ms': round(stats.min_response_time_ms, 2),
                    'max_response_time_ms': round(stats.max_response_time_ms, 2),
                    'p95_response_time_ms': round(stats.p95_response_time_ms, 2),
                    'p99_response_time_ms': round(stats.p99_response_time_ms, 2),
                    'avg_memory_usage_mb': round(stats.avg_memory_usage_mb, 2),
                    'peak_memory_usage_mb': round(stats.peak_memory_usage_mb, 2),
                    'avg_memory_delta_mb': round(stats.avg_memory_delta_mb, 4),
                    'window_start': stats.window_start.isoformat(),
                    'window_end': stats.window_end.isoformat() if stats.window_end else None
                },
                'system_stats': system_stats,
                'endpoint_stats': stats.endpoint_stats,
                'recent_requests': request_data,
                'active_requests': len(self._active_requests)
            }
    
    def _get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return 0.0
    
    def _monitor_system(self):
        """Background thread to monitor system performance"""
        while self._monitoring_active:
            try:
                # Update system statistics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                with self._lock:
                    self._system_stats.update({
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_available_mb': memory.available / 1024 / 1024,
                        'disk_usage_percent': disk.percent,
                        'last_updated': time.time()
                    })
                
                # Sleep for 30 seconds before next update
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(60)  # Wait longer on error
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring_active = False
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
    
    def reset_stats(self):
        """Reset all performance statistics"""
        with self._lock:
            self._request_history.clear()
            self._active_requests.clear()
            logger.info("Performance statistics reset")
    
    @contextmanager
    def track_request(self, request_id: str, endpoint: str, method: str = "POST"):
        """
        Context manager for tracking request performance
        
        Args:
            request_id: Unique request identifier
            endpoint: API endpoint
            method: HTTP method
        """
        metrics = self.start_request(request_id, endpoint, method)
        try:
            yield metrics
            self.complete_request(request_id, 200)  # Default success
        except Exception as e:
            self.complete_request(request_id, 500, error=str(e))
            raise


def performance_monitor_decorator(endpoint: str):
    """
    Decorator for automatically tracking function performance
    
    Args:
        endpoint: Endpoint name for tracking
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            request_id = kwargs.get('request_id', f"auto_{int(time.time() * 1000)}")
            
            with get_performance_monitor().track_request(request_id, endpoint):
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            request_id = kwargs.get('request_id', f"auto_{int(time.time() * 1000)}")
            
            with get_performance_monitor().track_request(request_id, endpoint):
                return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global performance monitor instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor instance (singleton pattern)
    
    Returns:
        PerformanceMonitor instance
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def reset_performance_monitor():
    """Reset the global performance monitor (useful for testing)"""
    global _performance_monitor
    if _performance_monitor:
        _performance_monitor.stop_monitoring()
    _performance_monitor = None