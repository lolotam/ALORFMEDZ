"""
Optimized JSON Database Layer with Caching and Performance Enhancements
"""

import json
import os
import secrets
import string
import threading
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from functools import lru_cache
from collections import defaultdict
import weakref
import hashlib

# Thread-safe file locking
_file_locks = defaultdict(threading.RLock)

class DatabaseCache:
    """In-memory cache with TTL and memory limits"""

    def __init__(self, max_size=1000, default_ttl=300):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]
            if time.time() > entry['expires']:
                del self.cache[key]
                del self.access_times[key]
                return None

            self.access_times[key] = time.time()
            return entry['data']

    def set(self, key: str, data: Any, ttl: int = None) -> None:
        with self._lock:
            if len(self.cache) >= self.max_size:
                self._evict_lru()

            ttl = ttl or self.default_ttl
            self.cache[key] = {
                'data': data,
                'expires': time.time() + ttl
            }
            self.access_times[key] = time.time()

    def invalidate(self, key: str) -> None:
        with self._lock:
            self.cache.pop(key, None)
            self.access_times.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self.cache.clear()
            self.access_times.clear()

    def _evict_lru(self) -> None:
        """Remove least recently used item"""
        if not self.access_times:
            return

        lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        del self.cache[lru_key]
        del self.access_times[lru_key]

# Global cache instance
_cache = DatabaseCache()

class OptimizedDatabase:
    """High-performance JSON database with caching and indexing"""

    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.db_files = {
            'users': os.path.join(data_dir, 'users.json'),
            'medicines': os.path.join(data_dir, 'medicines.json'),
            'patients': os.path.join(data_dir, 'patients.json'),
            'doctors': os.path.join(data_dir, 'doctors.json'),
            'suppliers': os.path.join(data_dir, 'suppliers.json'),
            'departments': os.path.join(data_dir, 'departments.json'),
            'stores': os.path.join(data_dir, 'stores.json'),
            'purchases': os.path.join(data_dir, 'purchases.json'),
            'consumption': os.path.join(data_dir, 'consumption.json'),
            'history': os.path.join(data_dir, 'history.json'),
            'transfers': os.path.join(data_dir, 'transfers.json')
        }
        self._indexes = {}
        self._file_hashes = {}

    def _get_file_hash(self, file_path: str) -> str:
        """Get file content hash for cache invalidation"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except FileNotFoundError:
            return ''

    def _is_cache_valid(self, file_type: str) -> bool:
        """Check if cached data is still valid"""
        file_path = self.db_files.get(file_type)
        if not file_path or not os.path.exists(file_path):
            return False

        current_hash = self._get_file_hash(file_path)
        cached_hash = self._file_hashes.get(file_type)

        return current_hash == cached_hash

    def load_data(self, file_type: str, use_cache: bool = True) -> List[Dict]:
        """Load data with intelligent caching"""
        cache_key = f"data_{file_type}"

        # Try cache first
        if use_cache and self._is_cache_valid(file_type):
            cached_data = _cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        file_path = self.db_files.get(file_type)
        if not file_path or not os.path.exists(file_path):
            return []

        # Use file locking for thread safety
        with _file_locks[file_path]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Update cache and hash
                if use_cache:
                    _cache.set(cache_key, data, ttl=600)  # 10 minutes TTL
                    self._file_hashes[file_type] = self._get_file_hash(file_path)

                return data

            except (json.JSONDecodeError, FileNotFoundError):
                return []

    def save_data(self, file_type: str, data: List[Dict], update_cache: bool = True) -> bool:
        """Save data with optimized writes and cache management"""
        file_path = self.db_files.get(file_type)
        if not file_path:
            return False

        with _file_locks[file_path]:
            try:
                # Create backup
                backup_path = f"{file_path}.backup"
                if os.path.exists(file_path):
                    os.rename(file_path, backup_path)

                # Write new data
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                # Update cache
                if update_cache:
                    cache_key = f"data_{file_type}"
                    _cache.set(cache_key, data, ttl=600)
                    self._file_hashes[file_type] = self._get_file_hash(file_path)

                # Remove backup on success
                if os.path.exists(backup_path):
                    os.remove(backup_path)

                return True

            except Exception as e:
                # Restore backup on failure
                backup_path = f"{file_path}.backup"
                if os.path.exists(backup_path):
                    os.rename(backup_path, file_path)
                print(f"Error saving data: {e}")
                return False

    def find_by_id(self, file_type: str, entity_id: str, use_index: bool = True) -> Optional[Dict]:
        """Optimized single record lookup with indexing"""
        if use_index:
            index_key = f"index_{file_type}_id"
            index = _cache.get(index_key)

            if index is None:
                # Build index
                data = self.load_data(file_type)
                index = {item.get('id'): item for item in data if item.get('id')}
                _cache.set(index_key, index, ttl=600)

            return index.get(entity_id)
        else:
            # Fallback to linear search
            data = self.load_data(file_type)
            return next((item for item in data if item.get('id') == entity_id), None)

    def find_by_field(self, file_type: str, field: str, value: Any) -> List[Dict]:
        """Optimized field-based search with indexing"""
        index_key = f"index_{file_type}_{field}"
        index = _cache.get(index_key)

        if index is None:
            # Build field index
            data = self.load_data(file_type)
            index = defaultdict(list)
            for item in data:
                field_value = item.get(field)
                if field_value is not None:
                    index[field_value].append(item)
            _cache.set(index_key, dict(index), ttl=600)

        return index.get(value, [])

    def paginate_data(self, file_type: str, page: int = 1, per_page: int = 50,
                     filters: Dict = None, sort_by: str = None, sort_desc: bool = False) -> Dict:
        """Paginated data loading with filtering and sorting"""
        data = self.load_data(file_type)

        # Apply filters
        if filters:
            filtered_data = []
            for item in data:
                match = True
                for field, value in filters.items():
                    if item.get(field) != value:
                        match = False
                        break
                if match:
                    filtered_data.append(item)
            data = filtered_data

        # Apply sorting
        if sort_by:
            try:
                data.sort(key=lambda x: x.get(sort_by, ''), reverse=sort_desc)
            except (TypeError, KeyError):
                pass  # Skip sorting if field doesn't exist or isn't comparable

        # Calculate pagination
        total = len(data)
        total_pages = (total + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        return {
            'data': data[start_idx:end_idx],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages
            }
        }

    def bulk_update(self, file_type: str, updates: List[Dict]) -> bool:
        """Optimized bulk update operations"""
        data = self.load_data(file_type)
        id_to_index = {item.get('id'): idx for idx, item in enumerate(data) if item.get('id')}

        # Apply updates
        for update in updates:
            entity_id = update.get('id')
            if entity_id and entity_id in id_to_index:
                idx = id_to_index[entity_id]
                data[idx] = {**data[idx], **update}

        # Invalidate related caches
        self._invalidate_caches(file_type)

        return self.save_data(file_type, data)

    def bulk_delete(self, file_type: str, entity_ids: List[str]) -> bool:
        """Optimized bulk delete operations"""
        data = self.load_data(file_type)
        id_set = set(entity_ids)

        # Filter out deleted items
        filtered_data = [item for item in data if item.get('id') not in id_set]

        # Invalidate related caches
        self._invalidate_caches(file_type)

        return self.save_data(file_type, filtered_data)

    def _invalidate_caches(self, file_type: str) -> None:
        """Invalidate all related caches for a file type"""
        _cache.invalidate(f"data_{file_type}")

        # Invalidate indexes
        cache_keys_to_remove = []
        for key in _cache.cache.keys():
            if key.startswith(f"index_{file_type}_"):
                cache_keys_to_remove.append(key)

        for key in cache_keys_to_remove:
            _cache.invalidate(key)

    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        return {
            'cache_size': len(_cache.cache),
            'max_cache_size': _cache.max_size,
            'cache_hit_ratio': self._calculate_hit_ratio(),
            'active_indexes': len([k for k in _cache.cache.keys() if k.startswith('index_')])
        }

    def _calculate_hit_ratio(self) -> float:
        """Calculate cache hit ratio (simplified)"""
        # This would need hit/miss counters for accurate calculation
        return 0.0  # Placeholder

# Global optimized database instance
optimized_db = OptimizedDatabase()

# Optimized helper functions that replace the original database.py functions
def load_data_optimized(file_type: str, use_cache: bool = True) -> List[Dict]:
    """Drop-in replacement for load_data with optimization"""
    return optimized_db.load_data(file_type, use_cache)

def save_data_optimized(file_type: str, data: List[Dict]) -> bool:
    """Drop-in replacement for save_data with optimization"""
    return optimized_db.save_data(file_type, data)

def find_by_id_optimized(file_type: str, entity_id: str) -> Optional[Dict]:
    """Optimized entity lookup by ID"""
    return optimized_db.find_by_id(file_type, entity_id)

def paginate_optimized(file_type: str, page: int = 1, per_page: int = 50, **kwargs) -> Dict:
    """Optimized pagination with filtering and sorting"""
    return optimized_db.paginate_data(file_type, page, per_page, **kwargs)