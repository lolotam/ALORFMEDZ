"""
Advanced Pagination and Memory Management Utilities
"""

from typing import List, Dict, Any, Optional, Tuple
from math import ceil
import json
from flask import request, url_for

class PaginationConfig:
    """Configuration for pagination settings"""
    DEFAULT_PER_PAGE = 25
    MAX_PER_PAGE = 100
    MIN_PER_PAGE = 5

class LazyDataLoader:
    """Lazy loading implementation for large datasets"""

    def __init__(self, data_source: str, loader_func, chunk_size: int = 1000):
        self.data_source = data_source
        self.loader_func = loader_func
        self.chunk_size = chunk_size
        self._cache = {}
        self._total_count = None

    def get_chunk(self, start_idx: int, end_idx: int) -> List[Dict]:
        """Load a specific chunk of data"""
        chunk_key = f"{start_idx}_{end_idx}"

        if chunk_key not in self._cache:
            # Calculate which chunk(s) we need
            start_chunk = start_idx // self.chunk_size
            end_chunk = end_idx // self.chunk_size

            # Load all necessary chunks
            data = []
            for chunk_idx in range(start_chunk, end_chunk + 1):
                chunk_start = chunk_idx * self.chunk_size
                chunk_end = min(chunk_start + self.chunk_size, self.get_total_count())

                if chunk_start < self.get_total_count():
                    chunk_data = self.loader_func(self.data_source, chunk_start, chunk_end - chunk_start)
                    data.extend(chunk_data)

            # Extract only the requested range
            relative_start = start_idx % self.chunk_size
            relative_end = relative_start + (end_idx - start_idx)
            self._cache[chunk_key] = data[relative_start:relative_end]

        return self._cache[chunk_key]

    def get_total_count(self) -> int:
        """Get total count of items"""
        if self._total_count is None:
            # This would be optimized to get count without loading all data
            self._total_count = len(self.loader_func(self.data_source))
        return self._total_count

class AdvancedPaginator:
    """High-performance paginator with memory optimization"""

    def __init__(self, data: List[Dict] = None, per_page: int = None,
                 data_loader: LazyDataLoader = None):
        self.data = data
        self.data_loader = data_loader
        self.per_page = self._validate_per_page(per_page)
        self._total = None

    def _validate_per_page(self, per_page: int) -> int:
        """Validate and normalize per_page parameter"""
        if per_page is None:
            return PaginationConfig.DEFAULT_PER_PAGE

        return max(
            PaginationConfig.MIN_PER_PAGE,
            min(per_page, PaginationConfig.MAX_PER_PAGE)
        )

    @property
    def total(self) -> int:
        """Get total number of items"""
        if self._total is None:
            if self.data_loader:
                self._total = self.data_loader.get_total_count()
            else:
                self._total = len(self.data) if self.data else 0
        return self._total

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages"""
        return ceil(self.total / self.per_page) if self.total > 0 else 1

    def get_page(self, page: int) -> Dict[str, Any]:
        """Get a specific page of data with metadata"""
        page = max(1, min(page, self.total_pages))

        start_idx = (page - 1) * self.per_page
        end_idx = min(start_idx + self.per_page, self.total)

        # Load data
        if self.data_loader:
            page_data = self.data_loader.get_chunk(start_idx, end_idx)
        else:
            page_data = self.data[start_idx:end_idx] if self.data else []

        return {
            'data': page_data,
            'pagination': {
                'page': page,
                'per_page': self.per_page,
                'total': self.total,
                'total_pages': self.total_pages,
                'has_prev': page > 1,
                'has_next': page < self.total_pages,
                'prev_page': page - 1 if page > 1 else None,
                'next_page': page + 1 if page < self.total_pages else None,
                'start_index': start_idx + 1,
                'end_index': end_idx
            }
        }

class SmartFilter:
    """Intelligent filtering with performance optimization"""

    def __init__(self, data: List[Dict]):
        self.data = data
        self._field_indexes = {}

    def _build_field_index(self, field: str) -> Dict:
        """Build index for a specific field"""
        if field not in self._field_indexes:
            index = {}
            for i, item in enumerate(self.data):
                value = item.get(field)
                if value is not None:
                    if value not in index:
                        index[value] = []
                    index[value].append(i)
            self._field_indexes[field] = index
        return self._field_indexes[field]

    def filter_by_field(self, field: str, value: Any) -> List[Dict]:
        """Fast field-based filtering using indexes"""
        index = self._build_field_index(field)
        indices = index.get(value, [])
        return [self.data[i] for i in indices]

    def filter_by_text_search(self, search_term: str, fields: List[str]) -> List[Dict]:
        """Optimized text search across multiple fields"""
        search_term = search_term.lower()
        results = []

        for item in self.data:
            found = False
            for field in fields:
                field_value = str(item.get(field, '')).lower()
                if search_term in field_value:
                    found = True
                    break
            if found:
                results.append(item)

        return results

    def apply_filters(self, filters: Dict[str, Any]) -> List[Dict]:
        """Apply multiple filters efficiently"""
        if not filters:
            return self.data

        result_sets = []

        for field, value in filters.items():
            if value:  # Skip empty filters
                if field == '_search':
                    # Special handling for text search
                    search_fields = filters.get('_search_fields', ['name'])
                    filtered = self.filter_by_text_search(value, search_fields)
                else:
                    filtered = self.filter_by_field(field, value)
                result_sets.append(set(id(item) for item in filtered))

        if not result_sets:
            return self.data

        # Intersection of all filter results
        common_ids = set.intersection(*result_sets)
        return [item for item in self.data if id(item) in common_ids]

def create_pagination_response(data: List[Dict], page: int, per_page: int,
                             endpoint: str, **url_params) -> Dict:
    """Create a complete pagination response with navigation URLs"""
    paginator = AdvancedPaginator(data, per_page)
    page_data = paginator.get_page(page)

    # Generate navigation URLs
    pagination_info = page_data['pagination']

    def build_url(page_num):
        params = {**url_params, 'page': page_num, 'per_page': per_page}
        return url_for(endpoint, **params)

    pagination_info['urls'] = {
        'first': build_url(1),
        'last': build_url(pagination_info['total_pages']),
        'prev': build_url(pagination_info['prev_page']) if pagination_info['has_prev'] else None,
        'next': build_url(pagination_info['next_page']) if pagination_info['has_next'] else None,
        'current': build_url(page)
    }

    return page_data

def optimize_large_dataset_loading(file_type: str, chunk_size: int = 1000) -> LazyDataLoader:
    """Create a lazy loader for large datasets"""
    def chunk_loader(source: str, start: int = 0, limit: int = None):
        from utils.optimized_database import optimized_db
        data = optimized_db.load_data(source)
        if limit:
            return data[start:start + limit]
        return data[start:]

    return LazyDataLoader(file_type, chunk_loader, chunk_size)

class DataViewOptimizer:
    """Optimize data presentation for frontend"""

    @staticmethod
    def optimize_for_table_view(data: List[Dict], visible_fields: List[str]) -> List[Dict]:
        """Extract only visible fields for table display"""
        return [
            {field: item.get(field) for field in visible_fields if field in item}
            for item in data
        ]

    @staticmethod
    def prepare_select_options(data: List[Dict], value_field: str = 'id',
                             label_field: str = 'name') -> List[Dict]:
        """Prepare data for select dropdown options"""
        return [
            {
                'value': item.get(value_field),
                'label': item.get(label_field, f"Item {item.get(value_field)}")
            }
            for item in data
            if item.get(value_field) is not None
        ]

    @staticmethod
    def compress_response_data(data: Any) -> str:
        """Compress response data for large payloads"""
        import gzip
        import base64

        json_str = json.dumps(data, separators=(',', ':'))
        compressed = gzip.compress(json_str.encode('utf-8'))
        return base64.b64encode(compressed).decode('ascii')

def get_request_pagination_params() -> Tuple[int, int]:
    """Extract pagination parameters from Flask request"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', PaginationConfig.DEFAULT_PER_PAGE, type=int)

    # Validate parameters
    page = max(1, page)
    per_page = max(
        PaginationConfig.MIN_PER_PAGE,
        min(per_page, PaginationConfig.MAX_PER_PAGE)
    )

    return page, per_page

def create_ajax_pagination_response(data: List[Dict], page: int, per_page: int) -> Dict:
    """Create AJAX-friendly pagination response"""
    paginator = AdvancedPaginator(data, per_page)
    page_data = paginator.get_page(page)

    return {
        'success': True,
        'data': page_data['data'],
        'pagination': page_data['pagination'],
        'meta': {
            'timestamp': int(time.time()),
            'cached': False  # Could be enhanced to indicate cache hits
        }
    }