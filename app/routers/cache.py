"""
Cache Statistics and Management Router
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.utils.cache_manager import get_cache_manager
from app.models.responses import ErrorResponse

router = APIRouter(
    prefix="/cache",
    tags=["cache"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.get("/stats", summary="Get cache statistics")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get comprehensive cache statistics including hit rates, size, and performance metrics
    
    Returns:
        Dictionary containing cache statistics
    """
    try:
        cache_manager = get_cache_manager()
        stats = cache_manager.get_stats()
        
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "cache_stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cache statistics: {str(e)}"
        )


@router.get("/info", summary="Get detailed cache information")
async def get_cache_info(
    include_entries: bool = Query(False, description="Include detailed entry information")
) -> Dict[str, Any]:
    """
    Get detailed cache information including entry details
    
    Args:
        include_entries: Whether to include detailed entry information
        
    Returns:
        Dictionary containing detailed cache information
    """
    try:
        cache_manager = get_cache_manager()
        
        if include_entries:
            info = cache_manager.get_cache_info()
        else:
            info = {"stats": cache_manager.get_stats()}
        
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "cache_info": info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cache information: {str(e)}"
        )


@router.get("/memory", summary="Get cache memory usage estimate")
async def get_cache_memory_usage() -> Dict[str, Any]:
    """
    Get estimated memory usage of the cache
    
    Returns:
        Dictionary containing memory usage estimates
    """
    try:
        cache_manager = get_cache_manager()
        memory_info = cache_manager.get_memory_usage_estimate()
        
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "memory_usage": memory_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve cache memory usage: {str(e)}"
        )


@router.post("/optimize", summary="Optimize cache performance")
async def optimize_cache() -> Dict[str, Any]:
    """
    Perform cache optimization by removing expired entries and least used entries
    
    Returns:
        Dictionary containing optimization results
    """
    try:
        cache_manager = get_cache_manager()
        optimization_result = cache_manager.optimize_cache()
        
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "optimization_result": optimization_result,
            "message": "Cache optimization completed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize cache: {str(e)}"
        )


@router.post("/resize", summary="Resize cache maximum size")
async def resize_cache(
    new_size: int = Query(..., ge=1, le=10000, description="New maximum cache size")
) -> Dict[str, Any]:
    """
    Resize the cache to a new maximum size
    
    Args:
        new_size: New maximum cache size (1-10000)
        
    Returns:
        Dictionary containing resize operation results
    """
    try:
        cache_manager = get_cache_manager()
        resize_result = cache_manager.resize_cache(new_size)
        
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "resize_result": resize_result,
            "message": f"Cache resized to maximum {new_size} entries"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resize cache: {str(e)}"
        )


@router.delete("/clear", summary="Clear all cache entries")
async def clear_cache() -> Dict[str, Any]:
    """
    Clear all entries from the cache
    
    Returns:
        Dictionary containing clear operation results
    """
    try:
        cache_manager = get_cache_manager()
        
        # Get stats before clearing
        stats_before = cache_manager.get_stats()
        entries_before = stats_before['size']
        
        # Clear the cache
        cache_manager.clear()
        
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "cleared_entries": entries_before,
            "message": f"Successfully cleared {entries_before} cache entries"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.delete("/entry/{key_hash}", summary="Delete specific cache entry")
async def delete_cache_entry(key_hash: str) -> Dict[str, Any]:
    """
    Delete a specific cache entry by key hash
    
    Args:
        key_hash: Hash of the cache key to delete
        
    Returns:
        Dictionary containing delete operation results
    """
    try:
        cache_manager = get_cache_manager()
        
        # Try to find and delete the entry
        # Since we only have the hash, we need to find matching keys
        deleted = False
        for cache_key in list(cache_manager._cache.keys()):
            if key_hash in cache_key:
                deleted = cache_manager.delete(cache_key)
                break
        
        if deleted:
            message = f"Successfully deleted cache entry with hash: {key_hash}"
        else:
            message = f"No cache entry found with hash: {key_hash}"
        
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "deleted": deleted,
            "message": message
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete cache entry: {str(e)}"
        )