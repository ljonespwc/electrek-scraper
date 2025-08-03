"""
Simple file-based caching service for chart data
"""
import json
import hashlib
import os
from datetime import datetime, timedelta

class ChartDataCache:
    """Simple file-based cache for chart data with 1-month TTL"""
    
    def __init__(self, cache_dir='static/cache', ttl_days=30):
        self.cache_dir = cache_dir
        self.ttl_days = ttl_days
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, data_type, months=None):
        """Generate cache key based on data type and parameters"""
        key_data = f"{data_type}_{months or 'all'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key):
        """Get full path to cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _is_cache_valid(self, cache_path):
        """Check if cache file exists and is within TTL"""
        if not os.path.exists(cache_path):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        expire_time = datetime.now() - timedelta(days=self.ttl_days)
        return file_time > expire_time
    
    def get(self, data_type, months=None):
        """Get cached data if valid"""
        cache_key = self._get_cache_key(data_type, months)
        cache_path = self._get_cache_path(cache_key)
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return None
    
    def set(self, data_type, data, months=None):
        """Cache data with timestamp"""
        cache_key = self._get_cache_key(data_type, months)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, default=str)
        except IOError:
            pass  # Fail silently if cache write fails