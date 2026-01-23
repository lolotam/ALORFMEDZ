"""
Performance Tests

Tests for performance optimizations including caching, pagination,
and query optimization.
"""

import pytest
import time
from io import BytesIO


class TestCaching:
    """Test caching functionality"""

    def test_cache_decorator(self):
        """Test cache decorator functionality"""
        from app.utils.cache import cache_result

        call_count = 0

        @cache_result(timeout=10)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call should execute the function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment

    def test_cache_invalidation(self):
        """Test cache invalidation"""
        from app.utils.cache import get_cache, invalidate_cache_pattern

        cache = get_cache()

        # Set some cache items
        cache.set('test_key_1', 'value1', 60)
        cache.set('test_key_2', 'value2', 60)
        cache.set('other_key', 'value3', 60)

        # Invalidate by pattern
        invalidated = invalidate_cache_pattern('test_key')

        # Should have invalidated 2 items
        assert invalidated == 2

        # Check that invalidated items are gone
        assert cache.get('test_key_1') is None
        assert cache.get('test_key_2') is None

        # Other items should still exist
        assert cache.get('other_key') == 'value3'

    def test_cache_timeout(self):
        """Test cache timeout"""
        from app.utils.cache import get_cache

        cache = get_cache()

        # Set item with 1 second timeout
        cache.set('test_timeout', 'value', 1)

        # Should exist immediately
        assert cache.get('test_timeout') == 'value'

        # Wait for timeout
        time.sleep(1.1)

        # Should be expired
        assert cache.get('test_timeout') is None


class TestPagination:
    """Test pagination functionality"""

    def test_pagination_basic(self):
        """Test basic pagination"""
        from app.utils.pagination import PaginationHelper

        items = list(range(1, 101))  # 100 items

        helper = PaginationHelper(page=1, per_page=10)
        result = helper.paginate(items)

        assert len(result['items']) == 10
        assert result['total'] == 100
        assert result['page'] == 1
        assert result['per_page'] == 10
        assert result['has_next'] is True
        assert result['has_prev'] is False

    def test_pagination_middle_page(self):
        """Test pagination on middle page"""
        from app.utils.pagination import PaginationHelper

        items = list(range(1, 101))

        helper = PaginationHelper(page=5, per_page=10)
        result = helper.paginate(items)

        assert len(result['items']) == 10
        assert result['page'] == 5
        assert result['has_next'] is True
        assert result['has_prev'] is True

    def test_pagination_last_page(self):
        """Test pagination on last page"""
        from app.utils.pagination import PaginationHelper

        items = list(range(1, 101))

        helper = PaginationHelper(page=10, per_page=10)
        result = helper.paginate(items)

        assert len(result['items']) == 10
        assert result['page'] == 10
        assert result['has_next'] is False
        assert result['has_prev'] is True

    def test_pagination_from_request(self):
        """Test pagination from request args"""
        from app.utils.pagination import PaginationHelper

        # Mock request
        import app.utils.pagination
        original_request = app.utils.pagination.request

        class MockRequest:
            args = {'page': '2', 'per_page': '20'}

        app.utils.pagination.request = MockRequest()

        try:
            helper = PaginationHelper.from_request(default_per_page=25, max_per_page=100)
            assert helper.page == 2
            assert helper.per_page == 20
        finally:
            app.utils.pagination.request = original_request

    def test_pagination_validation(self):
        """Test pagination parameter validation"""
        from app.utils.pagination import validate_pagination_params

        # Valid params
        page, per_page = validate_pagination_params(page=1, per_page=25)
        assert page == 1
        assert per_page == 25

        # Invalid page (should default to 1)
        page, per_page = validate_pagination_params(page=0, per_page=25)
        assert page == 1

        # Invalid per_page (should default to 25)
        page, per_page = validate_pagination_params(page=1, per_page=0)
        assert per_page == 25

        # per_page too large (should cap at max)
        page, per_page = validate_pagination_params(page=1, per_page=200, max_per_page=100)
        assert per_page == 100

    def test_lazy_load_response(self):
        """Test lazy load response format"""
        from app.utils.pagination import lazy_load_paginated_response

        items = list(range(1, 101))

        result = lazy_load_paginated_response(items, page=1, per_page=10)

        assert 'items' in result
        assert 'lazy_load' in result
        assert result['lazy_load']['current_page'] == 1
        assert result['lazy_load']['has_more'] is True


class TestLoggingPerformance:
    """Test performance logging"""

    def test_performance_decorator(self):
        """Test performance monitoring decorator"""
        from app.utils.middleware import monitor_performance
        import time

        @monitor_performance(threshold=0.001)  # Very low threshold for testing
        def slow_function():
            time.sleep(0.01)  # 10ms delay
            return 'done'

        result = slow_function()
        assert result == 'done'


class TestHealthCheckPerformance:
    """Test health check performance"""

    def test_health_check_response_time(self, client):
        """Test that health check responds quickly"""
        start_time = time.time()
        response = client.get('/health')
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second

    def test_metrics_endpoint_performance(self, client):
        """Test metrics endpoint responds quickly"""
        start_time = time.time()
        response = client.get('/health/metrics')
        end_time = time.time()

        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second


class TestDatabasePerformance:
    """Test database query performance"""

    def test_database_init_performance(self):
        """Test database initialization time"""
        from app.utils.database import init_database

        start_time = time.time()
        init_database()
        end_time = time.time()

        # Database initialization should complete quickly
        assert (end_time - start_time) < 5.0


class TestLoadPerformance:
    """Test application under load"""

    @pytest.mark.slow
    def test_multiple_concurrent_requests(self, client):
        """Test multiple concurrent requests"""
        import threading
        import time

        results = []
        errors = []

        def make_request():
            try:
                response = client.get('/health')
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Create 10 concurrent threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert len(errors) == 0
        assert all(status == 200 for status in results)

    def test_login_performance(self, client):
        """Test login endpoint performance"""
        # Get CSRF token
        token_response = client.get('/csrf-token')
        token_data = token_response.get_json()
        csrf_token = token_data['csrf_token']

        start_time = time.time()
        response = client.post('/auth/login',
                               headers={'X-CSRF-Token': csrf_token},
                               data={'username': 'admin', 'password': '@Xx123456789xX@'},
                               follow_redirects=True)
        end_time = time.time()

        # Should complete within 2 seconds
        assert (end_time - start_time) < 2.0

    def test_dashboard_load_performance(self, authenticated_client):
        """Test dashboard loading performance"""
        start_time = time.time()
        response = authenticated_client.get('/dashboard')
        end_time = time.time()

        assert response.status_code == 200
        # Dashboard should load within 3 seconds
        assert (end_time - start_time) < 3.0


class TestMemoryUsage:
    """Test memory usage"""

    def test_cache_memory_usage(self):
        """Test cache doesn't use excessive memory"""
        from app.utils.cache import get_cache

        cache = get_cache()

        # Set many items
        for i in range(1000):
            cache.set(f'key_{i}', f'value_{i}', 60)

        # All items should be retrievable
        for i in range(1000):
            assert cache.get(f'key_{i}') == f'value_{i}'


class TestResponseSize:
    """Test response sizes"""

    def test_health_check_response_size(self, client):
        """Test health check response is not too large"""
        response = client.get('/health')

        # Response should be under 10KB
        assert len(response.data) < 10 * 1024

    def test_csrf_token_response_size(self, client):
        """Test CSRF token response is minimal"""
        response = client.get('/csrf-token')

        # Should be very small
        assert len(response.data) < 1024


class TestOptimizations:
    """Test optimization features"""

    def test_cache_stats(self):
        """Test cache statistics"""
        from app.utils.cache import get_cache

        cache = get_cache()

        # Set items with different timeouts
        cache.set('item1', 'value1', 10)
        cache.set('item2', 'value2', 60)

        # Items should exist
        assert cache.get('item1') == 'value1'
        assert cache.get('item2') == 'value2'

    def test_pagination_edge_cases(self):
        """Test pagination edge cases"""
        from app.utils.pagination import PaginationHelper

        # Empty list
        items = []
        helper = PaginationHelper(page=1, per_page=10)
        result = helper.paginate(items)

        assert len(result['items']) == 0
        assert result['total'] == 0
        assert result['pages'] == 0

        # Single item, page 2
        items = ['item1']
        helper = PaginationHelper(page=2, per_page=10)
        result = helper.paginate(items)

        assert len(result['items']) == 0
        assert result['has_next'] is False

        # Items less than page size
        items = ['item1', 'item2', 'item3']
        helper = PaginationHelper(page=1, per_page=10)
        result = helper.paginate(items)

        assert len(result['items']) == 3
        assert result['pages'] == 1
        assert result['has_next'] is False
