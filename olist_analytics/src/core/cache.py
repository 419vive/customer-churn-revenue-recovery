"""Enterprise caching layer for Olist Analytics"""

import pickle
import hashlib
import time
from typing import Any, Optional, Callable, Union
from functools import wraps
from pathlib import Path
import pandas as pd

from .config import config
from .logging import get_logger
from .exceptions import CacheError

logger = get_logger(__name__)

class CacheManager:
    """File-based cache manager with TTL support"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or config.project_root / '.cache'
        self.cache_dir.mkdir(exist_ok=True)
        self.enabled = config.cache.enabled
        
    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path from key"""
        # Create hash of key to avoid filesystem issues
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _is_expired(self, cache_path: Path, ttl: int) -> bool:
        """Check if cache file is expired"""
        if not cache_path.exists():
            return True
            
        file_age = time.time() - cache_path.stat().st_mtime
        return file_age > ttl
    
    def get(self, key: str, ttl: int = None) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
            
        cache_path = self._get_cache_path(key)
        ttl = ttl or config.cache.ttl_seconds
        
        try:
            if self._is_expired(cache_path, ttl):
                return None
                
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
                logger.logger.debug(f"Cache hit for key: {key}")
                return data
                
        except Exception as e:
            logger.logger.warning(f"Cache read failed for key {key}: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        if not self.enabled:
            return False
            
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            logger.logger.debug(f"Cache set for key: {key}")
            return True
            
        except Exception as e:
            logger.logger.error(f"Cache write failed for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        cache_path = self._get_cache_path(key)
        
        try:
            if cache_path.exists():
                cache_path.unlink()
                logger.logger.debug(f"Cache deleted for key: {key}")
            return True
        except Exception as e:
            logger.logger.error(f"Cache delete failed for key {key}: {str(e)}")
            return False
    
    def clear(self) -> int:
        """Clear all cache files"""
        deleted = 0
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
                deleted += 1
            logger.logger.info(f"Cache cleared: {deleted} files deleted")
        except Exception as e:
            logger.logger.error(f"Cache clear failed: {str(e)}")
            
        return deleted
    
    def size(self) -> dict:
        """Get cache size information"""
        try:
            cache_files = list(self.cache_dir.glob("*.cache"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                'file_count': len(cache_files),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / 1024 / 1024
            }
        except Exception as e:
            logger.logger.error(f"Cache size calculation failed: {str(e)}")
            return {'file_count': 0, 'total_size_bytes': 0, 'total_size_mb': 0}

# Global cache manager instance
cache_manager = CacheManager()

def cache_result(ttl: int = None, key_func: Optional[Callable] = None):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                cache_key = f"{func.__module__}.{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key, ttl)
            if cached_result is not None:
                return cached_result
            
            # Compute result and cache it
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def cache_dataframe(ttl: int = 3600):
    """Specialized decorator for caching pandas DataFrames"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key including DataFrame shapes if present
            df_signatures = []
            for arg in args:
                if isinstance(arg, pd.DataFrame):
                    df_signatures.append(f"df_{arg.shape}_{hash(str(arg.columns.tolist()))}")
                    
            cache_key = f"{func.__module__}.{func.__name__}:{'_'.join(df_signatures)}:{hash(str(kwargs))}"
            
            # Try cache
            cached_result = cache_manager.get(cache_key, ttl)
            if cached_result is not None:
                if isinstance(cached_result, pd.DataFrame):
                    logger.logger.debug(f"DataFrame cache hit: {cached_result.shape}")
                return cached_result
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            if isinstance(result, pd.DataFrame):
                logger.logger.debug(f"DataFrame cached: {result.shape}")
            
            return result
        return wrapper
    return decorator