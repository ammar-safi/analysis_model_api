"""
In-Memory Cache Manager for Sentiment and Stance Analysis Results
"""
import hashlib
import time
import logging
from typing import Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import threading
from dataclasses import dataclass

# Set up logger for cache operations
logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata"""
    data: Any
    created_at: float
    expires_at: float
    access_count: int = 0
    last_accessed: float = 0.0
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        return time.time() > self.expires_at
    
    def access(self) -> Any:
        """Mark entry as accessed and return data"""
        self.access_count += 1
        self.last_accessed = time.time()
        return self.data


class CacheManager:
    """
    Thread-safe in-memory cache manager for analysis results
    Supports TTL (Time To Live) and size-based eviction
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize cache manager
        
        Args:
            max_size: Maximum number of entries to store
            default_ttl: Default time-to-live in seconds (1 hour default)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        
        # Statistics
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_removals': 0,
            'manual_removals': 0
        }
        
        # Last cleanup time
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # Clean up every 5 minutes
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        with self._lock:
            # Periodic cleanup
            self._maybe_cleanup()
            
            if key not in self._cache:
                self._stats['misses'] += 1
                logger.debug(f"Cache MISS for key: {key[:50]}...")
                return None
            
            entry = self._cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self._cache[key]
                self._stats['expired_removals'] += 1
                self._stats['misses'] += 1
                logger.debug(f"Cache MISS (expired) for key: {key[:50]}...")
                return None
            
            # Cache hit
            self._stats['hits'] += 1
            logger.debug(f"Cache HIT for key: {key[:50]}... (access count: {entry.access_count + 1})")
            return entry.access()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            ttl = ttl or self.default_ttl
            current_time = time.time()
            
            # Create cache entry
            entry = CacheEntry(
                data=value,
                created_at=current_time,
                expires_at=current_time + ttl,
                last_accessed=current_time
            )
            
            # Check if we need to evict entries
            if len(self._cache) >= self.max_size and key not in self._cache:
                logger.info(f"Cache size limit reached ({self.max_size}), evicting entries...")
                self._evict_entries()
            
            self._cache[key] = entry
            logger.debug(f"Cache SET for key: {key[:50]}... (TTL: {ttl}s)")
    
    def delete(self, key: str) -> bool:
        """
        Delete entry from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was found and deleted, False otherwise
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats['manual_removals'] += 1
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            cleared_count = len(self._cache)
            self._cache.clear()
            self._stats['manual_removals'] += cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._stats['hits'] + self._stats['misses']
            hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._stats['hits'],
                'misses': self._stats['misses'],
                'hit_rate_percent': round(hit_rate, 2),
                'evictions': self._stats['evictions'],
                'expired_removals': self._stats['expired_removals'],
                'manual_removals': self._stats['manual_removals'],
                'total_requests': total_requests,
                'default_ttl_seconds': self.default_ttl
            }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get detailed cache information including entry details
        
        Returns:
            Dictionary with detailed cache information
        """
        with self._lock:
            current_time = time.time()
            entries_info = []
            
            for key, entry in self._cache.items():
                entries_info.append({
                    'key': key[:50] + '...' if len(key) > 50 else key,  # Truncate long keys
                    'created_at': datetime.fromtimestamp(entry.created_at).isoformat(),
                    'expires_at': datetime.fromtimestamp(entry.expires_at).isoformat(),
                    'ttl_remaining': max(0, int(entry.expires_at - current_time)),
                    'access_count': entry.access_count,
                    'last_accessed': datetime.fromtimestamp(entry.last_accessed).isoformat() if entry.last_accessed > 0 else 'Never',
                    'is_expired': entry.is_expired()
                })
            
            # Sort by creation time (newest first)
            entries_info.sort(key=lambda x: x['created_at'], reverse=True)
            
            return {
                'stats': self.get_stats(),
                'entries': entries_info[:20]  # Limit to first 20 entries for readability
            }
    
    def _evict_entries(self) -> None:
        """
        Evict entries when cache is full
        Uses LRU (Least Recently Used) strategy
        """
        if not self._cache:
            return
        
        # Calculate how many entries to evict (25% of max_size)
        evict_count = max(1, self.max_size // 4)
        
        # Sort entries by last accessed time (oldest first)
        entries_by_access = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Evict oldest entries
        evicted_keys = []
        for i in range(min(evict_count, len(entries_by_access))):
            key, _ = entries_by_access[i]
            del self._cache[key]
            self._stats['evictions'] += 1
            evicted_keys.append(key[:30] + '...' if len(key) > 30 else key)
        
        logger.info(f"Evicted {len(evicted_keys)} cache entries: {evicted_keys}")
    
    def _maybe_cleanup(self) -> None:
        """
        Perform periodic cleanup of expired entries
        """
        current_time = time.time()
        
        # Only cleanup if enough time has passed
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = current_time
        
        # Find and remove expired entries
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        if expired_keys:
            for key in expired_keys:
                del self._cache[key]
                self._stats['expired_removals'] += 1
            
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def resize_cache(self, new_max_size: int) -> Dict[str, Any]:
        """
        Resize the cache to a new maximum size
        
        Args:
            new_max_size: New maximum cache size
            
        Returns:
            Dictionary with resize operation results
        """
        with self._lock:
            old_size = self.max_size
            old_entry_count = len(self._cache)
            
            self.max_size = max(1, new_max_size)  # Ensure at least size 1
            
            # If new size is smaller, evict entries
            evicted_count = 0
            if len(self._cache) > self.max_size:
                # Sort by last accessed time and keep only the most recent entries
                entries_by_access = sorted(
                    self._cache.items(),
                    key=lambda x: x[1].last_accessed,
                    reverse=True  # Most recent first
                )
                
                # Keep only the entries that fit in the new size
                entries_to_keep = dict(entries_by_access[:self.max_size])
                evicted_count = len(self._cache) - len(entries_to_keep)
                
                self._cache = entries_to_keep
                self._stats['evictions'] += evicted_count
            
            result = {
                'old_max_size': old_size,
                'new_max_size': self.max_size,
                'old_entry_count': old_entry_count,
                'new_entry_count': len(self._cache),
                'evicted_entries': evicted_count
            }
            
            logger.info(f"Cache resized from {old_size} to {self.max_size}, evicted {evicted_count} entries")
            return result
    
    def get_memory_usage_estimate(self) -> Dict[str, Any]:
        """
        Get an estimate of cache memory usage
        
        Returns:
            Dictionary with memory usage estimates
        """
        with self._lock:
            import sys
            
            total_size = 0
            entry_sizes = []
            
            for key, entry in self._cache.items():
                key_size = sys.getsizeof(key)
                entry_size = sys.getsizeof(entry) + sys.getsizeof(entry.data)
                total_entry_size = key_size + entry_size
                
                total_size += total_entry_size
                entry_sizes.append(total_entry_size)
            
            avg_entry_size = sum(entry_sizes) / len(entry_sizes) if entry_sizes else 0
            
            return {
                'total_estimated_bytes': total_size,
                'total_estimated_mb': round(total_size / (1024 * 1024), 2),
                'entry_count': len(self._cache),
                'average_entry_size_bytes': round(avg_entry_size, 2),
                'largest_entry_size_bytes': max(entry_sizes) if entry_sizes else 0,
                'smallest_entry_size_bytes': min(entry_sizes) if entry_sizes else 0
            }
    
    def optimize_cache(self) -> Dict[str, Any]:
        """
        Perform cache optimization by removing expired entries and 
        least accessed entries if cache is getting full
        
        Returns:
            Dictionary with optimization results
        """
        with self._lock:
            initial_size = len(self._cache)
            
            # First, remove all expired entries
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
                self._stats['expired_removals'] += 1
            
            expired_removed = len(expired_keys)
            
            # If cache is still over 80% full, remove least accessed entries
            threshold = int(self.max_size * 0.8)
            lru_removed = 0
            
            if len(self._cache) > threshold:
                # Calculate how many to remove (bring down to 70% capacity)
                target_size = int(self.max_size * 0.7)
                entries_to_remove = len(self._cache) - target_size
                
                if entries_to_remove > 0:
                    # Sort by access count and last accessed time
                    entries_by_usage = sorted(
                        self._cache.items(),
                        key=lambda x: (x[1].access_count, x[1].last_accessed)
                    )
                    
                    # Remove least used entries
                    for i in range(min(entries_to_remove, len(entries_by_usage))):
                        key, _ = entries_by_usage[i]
                        del self._cache[key]
                        self._stats['evictions'] += 1
                        lru_removed += 1
            
            final_size = len(self._cache)
            
            result = {
                'initial_size': initial_size,
                'final_size': final_size,
                'expired_removed': expired_removed,
                'lru_removed': lru_removed,
                'total_removed': expired_removed + lru_removed,
                'cache_utilization_percent': round((final_size / self.max_size) * 100, 1)
            }
            
            logger.info(f"Cache optimized: removed {expired_removed} expired + {lru_removed} LRU entries")
            return result
    
    def generate_sentiment_key(self, text: str) -> str:
        """
        Generate cache key for sentiment analysis
        
        Args:
            text: Input text
            
        Returns:
            Cache key string
        """
        # Create hash of the text for consistent key generation
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"sentiment:{text_hash}"
    
    def generate_stance_key(self, text: str, target: str) -> str:
        """
        Generate cache key for stance analysis
        
        Args:
            text: Input text
            target: Target entity
            
        Returns:
            Cache key string
        """
        # Create hash of text + target combination
        combined = f"{text}|{target}"
        combined_hash = hashlib.md5(combined.encode('utf-8')).hexdigest()
        return f"stance:{combined_hash}"
        """
        Generate cache key for sentiment analysis
        
        Args:
            text: Input text
            
        Returns:
            Cache key string
        """
        # Create hash of the text for consistent key generation
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"sentiment:{text_hash}"
    
    def generate_stance_key(self, text: str, target: str) -> str:
        """
        Generate cache key for stance analysis
        
        Args:
            text: Input text
            target: Target entity
            
        Returns:
            Cache key string
        """
        # Create hash of text + target combination
        combined = f"{text}|{target}"
        combined_hash = hashlib.md5(combined.encode('utf-8')).hexdigest()
        return f"stance:{combined_hash}"


# Global cache instance
_cache_instance: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance (singleton pattern)
    
    Returns:
        CacheManager instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance


def reset_cache_manager() -> None:
    """Reset the global cache manager (useful for testing)"""
    global _cache_instance
    _cache_instance = None