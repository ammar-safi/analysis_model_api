"""
Performance Metrics and Monitoring Router
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import logging

from app.utils.performance_monitor import get_performance_monitor
from app.utils.cache_manager import get_cache_manager
from app.models.responses import ErrorResponse

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/metrics",
    tags=["monitoring"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


@router.get(
    "/performance",
    summary="Get performance metrics",
    description="Get detailed performance metrics including response times, memory usage, and system stats"
)
async def get_performance_metrics(
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Maximum number of recent requests to include"),
    detailed: bool = Query(False, description="Include detailed request history")
):
    """
    Get comprehensive performance metrics for the API.
    
    - **limit**: Maximum number of recent requests to include in detailed view
    - **detailed**: Whether to include detailed request history
    
    Returns performance statistics, system metrics, and optionally request history.
    """
    try:
        performance_monitor = get_performance_monitor()
        
        if detailed:
            metrics = performance_monitor.get_detailed_metrics(limit=limit)
        else:
            # Get basic stats without request history
            stats = performance_monitor.get_current_stats()
            system_stats = performance_monitor.get_system_stats()
            
            metrics = {
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
                    'window_start': stats.window_start.isoformat(),
                    'window_end': stats.window_end.isoformat() if stats.window_end else None
                },
                'system_stats': system_stats,
                'endpoint_stats': stats.endpoint_stats
            }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve performance metrics"
        )


@router.get(
    "/cache",
    summary="Get cache metrics",
    description="Get detailed cache performance metrics and statistics"
)
async def get_cache_metrics(
    detailed: bool = Query(False, description="Include detailed cache information")
):
    """
    Get cache performance metrics and statistics.
    
    - **detailed**: Whether to include detailed cache entry information
    
    Returns cache statistics, hit rates, and optionally entry details.
    """
    try:
        cache_manager = get_cache_manager()
        
        if detailed:
            metrics = cache_manager.get_cache_info()
        else:
            metrics = {
                'stats': cache_manager.get_stats(),
                'memory_usage': cache_manager.get_memory_usage_estimate()
            }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get cache metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve cache metrics"
        )


@router.get(
    "/system",
    summary="Get system metrics",
    description="Get current system performance metrics including CPU, memory, and disk usage"
)
async def get_system_metrics():
    """
    Get current system performance metrics.
    
    Returns CPU usage, memory usage, disk usage, and other system statistics.
    """
    try:
        performance_monitor = get_performance_monitor()
        system_stats = performance_monitor.get_system_stats()
        
        # Add additional system information
        try:
            import psutil
            
            # Get more detailed system info
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            boot_time = psutil.boot_time()
            
            system_stats.update({
                'cpu_count': cpu_count,
                'cpu_frequency_mhz': cpu_freq.current if cpu_freq else None,
                'system_boot_time': boot_time,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            })
            
        except ImportError:
            logger.warning("psutil not available for detailed system metrics")
        
        return {
            'system_metrics': system_stats,
            'timestamp': performance_monitor.get_system_stats()['last_updated']
        }
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve system metrics"
        )


@router.post(
    "/reset",
    summary="Reset performance metrics",
    description="Reset all performance statistics and cache (admin operation)"
)
async def reset_metrics(
    reset_cache: bool = Query(False, description="Also reset cache statistics"),
    reset_performance: bool = Query(True, description="Reset performance statistics")
):
    """
    Reset performance metrics and optionally cache statistics.
    
    - **reset_cache**: Whether to also reset cache statistics
    - **reset_performance**: Whether to reset performance statistics
    
    This is an administrative operation that clears historical data.
    """
    try:
        results = {}
        
        if reset_performance:
            performance_monitor = get_performance_monitor()
            performance_monitor.reset_stats()
            results['performance_reset'] = True
            logger.info("Performance statistics reset")
        
        if reset_cache:
            cache_manager = get_cache_manager()
            cache_stats_before = cache_manager.get_stats()
            cache_manager.clear()
            results['cache_reset'] = True
            results['cache_entries_cleared'] = cache_stats_before['size']
            logger.info(f"Cache cleared: {cache_stats_before['size']} entries removed")
        
        return {
            'message': 'Metrics reset successfully',
            'operations_performed': results
        }
        
    except Exception as e:
        logger.error(f"Failed to reset metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to reset metrics"
        )


@router.post(
    "/cache/optimize",
    summary="Optimize cache performance",
    description="Perform cache optimization by removing expired and least-used entries"
)
async def optimize_cache():
    """
    Optimize cache performance by cleaning up expired entries and 
    removing least-used entries if cache is getting full.
    
    Returns optimization results including entries removed.
    """
    try:
        cache_manager = get_cache_manager()
        optimization_results = cache_manager.optimize_cache()
        
        logger.info(f"Cache optimized: {optimization_results}")
        
        return {
            'message': 'Cache optimization completed',
            'results': optimization_results
        }
        
    except Exception as e:
        logger.error(f"Failed to optimize cache: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to optimize cache"
        )