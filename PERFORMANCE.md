# Performance Documentation

## Overview

This document describes the performance optimizations implemented in the ALORF Hospital Pharmacy Management System. The application includes caching, pagination, query optimization, and performance monitoring to ensure optimal performance.

## Performance Features

### 1. Caching

**Implementation**: Simple in-memory cache with TTL support

**Location**: `app/utils/cache.py`

**Features**:
- Configurable TTL (Time To Live) for cache items
- Cache decorators for easy function caching
- Pattern-based cache invalidation
- Thread-safe operations
- Cache statistics

**Cache Strategies**:

#### Department Caching
```python
from app.utils.cache import cache_departments

@cache_departments
def get_departments():
    # Expensive database operation
    return fetch_departments_from_db()
```
- **TTL**: 1 hour
- **Invalidated on**: Department creation, update, deletion

#### Supplier Caching
```python
from app.utils.cache import cache_suppliers

@cache_suppliers
def get_suppliers():
    # Expensive database operation
    return fetch_suppliers_from_db()
```
- **TTL**: 1 hour
- **Invalidated on**: Supplier creation, update, deletion

#### Medicine Caching
```python
from app.utils.cache import cache_medicines

@cache_medicines
def get_medicines():
    # Expensive database operation
    return fetch_medicines_from_db()
```
- **TTL**: 30 minutes
- **Invalidated on**: Medicine creation, update, deletion

**Manual Cache Usage**:
```python
from app.utils.cache import get_cache

cache = get_cache()

# Set value
cache.set('user:123', user_data, timeout=3600)

# Get value
user = cache.get('user:123')

# Get or set (cache-aside pattern)
user = cache.get_or_set(
    'user:123',
    lambda: fetch_user_from_db(123),
    timeout=3600
)

# Invalidate by pattern
invalidate_cache_pattern('user:')
```

### 2. Pagination

**Implementation**: Flexible pagination helper

**Location**: `app/utils/pagination.py`

**Features**:
- Configurable page size (default: 25, max: 100)
- Lazy loading support
- Request-based pagination
- Validation of pagination parameters
- Metadata for pagination (total, pages, has_next, has_prev)

**Basic Usage**:
```python
from app.utils.pagination import PaginationHelper

items = list(range(1, 101))  # 100 items
helper = PaginationHelper(page=1, per_page=10)
result = helper.paginate(items)

print(result)
# {
#     'items': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
#     'total': 100,
#     'page': 1,
#     'per_page': 10,
#     'pages': 10,
#     'has_prev': False,
#     'has_next': True,
#     'prev_num': None,
#     'next_num': 2
# }
```

**From Request Args**:
```python
from app.utils.pagination import PaginationHelper

# Automatically reads page and per_page from request args
helper = PaginationHelper.from_request(default_per_page=25, max_per_page=100)
result = helper.paginate(items)
```

**Lazy Loading**:
```python
from app.utils.pagination import lazy_load_paginated_response

result = lazy_load_paginated_response(items, page=1, per_page=20)

# Includes lazy_load metadata
print(result['lazy_load'])
# {
#     'current_page': 1,
#     'next_page': 2,
#     'has_more': True,
#     'items_loaded': 20
# }
```

**Configuration** (in `.env`):
```bash
DEFAULT_PAGE_SIZE=25
MAX_PAGE_SIZE=100
```

### 3. Performance Monitoring

**Implementation**: Request/response timing and slow operation detection

**Location**: `app/utils/middleware.py`, `app/utils/logging_config.py`

**Features**:
- Request timing middleware
- Slow request detection (>2 seconds)
- Slow query detection (>1 second)
- Cache hit/miss logging
- Memory usage monitoring
- Performance metrics collection

**Automatic Monitoring**:
```python
# Automatically logs requests taking >2 seconds
@monitor_performance(threshold=2.0)
def expensive_operation():
    # Slow operation
    pass
```

**Metrics Collection**:
```python
from app.utils.logging_config import performance_logger

performance_logger.log_slow_query(
    query='SELECT * FROM patients',
    execution_time=1.5,
    threshold=1.0
)

performance_logger.log_cache_hit('user:123')
performance_logger.log_cache_miss('user:456')
```

### 4. Health Checks

**Implementation**: Comprehensive health monitoring

**Location**: `app/blueprints/health.py`

**Endpoints**:
- `/health` - Overall health status
- `/health/ready` - Readiness probe
- `/health/live` - Liveness probe
- `/health/metrics` - Performance metrics

**Health Check Response**:
```json
{
    "status": "healthy",
    "timestamp": 1234567890,
    "checks": {
        "database": {
            "status": "healthy",
            "response_time": 0.01
        },
        "file_system": {
            "status": "healthy"
        },
        "memory": {
            "status": "healthy",
            "usage_percent": 45.2,
            "available_gb": 8.5,
            "total_gb": 16.0
        },
        "disk": {
            "status": "healthy",
            "usage_percent": 65.1,
            "free_gb": 120.5,
            "total_gb": 250.0
        }
    },
    "version": "1.0.0",
    "uptime": {
        "seconds": 86400,
        "readable": "1d 0h 0m 0s",
        "boot_time": 1234483290
    }
}
```

### 5. Database Optimization

**Implementation**: Optimized database queries and operations

**Location**: `app/utils/database/`

**Features**:
- Minimal database reads
- Batch operations where possible
- Efficient file-based storage
- Read-modify-write pattern
- File locking for consistency

**Best Practices**:
```python
# Load data once, reuse
departments = get_departments()  # Cached
for dept in departments:
    process_department(dept)

# Use cache for frequently accessed data
cached_depts = cache_manager.get_departments()
if not cached_depts:
    cached_depts = get_departments()
    cache_manager.set_departments(cached_depts)
```

### 6. Template Rendering Optimization

**Features**:
- Jinja2 template caching
- Template fragments for reusability
- Minimal database queries in templates
- Static file caching in production

**Template Caching**:
```python
# Enabled in production configuration
TEMPLATE_CACHE_TIMEOUT=3600  # 1 hour
```

### 7. Static File Optimization

**Implementation**: Static file caching headers

**Configuration**:
```python
# In production config
SEND_FILE_MAX_AGE_DEFAULT=31536000  # 1 year cache for static files
```

**Features**:
- Long-term caching for static assets
- Proper cache headers
- Gzip compression (via web server)

## Performance Configuration

### Environment Variables

```bash
# Cache Configuration
CACHE_DEFAULT_TIMEOUT=3600
CACHE_DEPARTMENT_TIMEOUT=3600
CACHE_SUPPLIER_TIMEOUT=3600
CACHE_MEDICINE_TIMEOUT=1800

# Pagination
DEFAULT_PAGE_SIZE=25
MAX_PAGE_SIZE=100

# Template Cache
TEMPLATE_CACHE_TIMEOUT=3600

# Logging
LOG_LEVEL=INFO
```

### Production Configuration

```python
class ProductionConfig(Config):
    # Enable caching
    TEMPLATE_CACHE_TIMEOUT = 3600

    # Static file caching
    SEND_FILE_MAX_AGE_DEFAULT = 31536000

    # Disable debug
    DEBUG = False
```

## Performance Testing

### Running Performance Tests

```bash
# Run all performance tests
pytest tests/test_performance.py -v

# Run specific test
pytest tests/test_performance.py::TestCaching::test_cache_decorator -v

# Run tests with coverage
pytest tests/test_performance.py --cov=app.utils.cache --cov-report=html
```

### Performance Benchmarks

#### Expected Performance

| Operation | Expected Time | Acceptable Threshold |
|-----------|---------------|---------------------|
| Login | < 1 second | 2 seconds |
| Dashboard Load | < 2 seconds | 3 seconds |
| Medicine List (paginated) | < 1 second | 2 seconds |
| Department List (cached) | < 0.5 seconds | 1 second |
| Health Check | < 0.5 seconds | 1 second |
| Database Initialization | < 2 seconds | 5 seconds |

#### Cache Hit Rates

| Data Type | Expected Hit Rate | Minimum Acceptable |
|-----------|------------------|-------------------|
| Departments | > 90% | 80% |
| Suppliers | > 90% | 80% |
| Medicines | > 80% | 70% |
| User Data | > 85% | 75% |

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test health endpoint
ab -n 1000 -c 10 http://localhost:5045/health

# Test login endpoint (with proper credentials)
ab -n 100 -c 5 -p login_data.txt -T "application/x-www-form-urlencoded" \
   http://localhost:5045/auth/login
```

### Monitoring Performance

#### Key Metrics to Monitor

1. **Response Times**:
   - Average response time
   - 95th percentile response time
   - 99th percentile response time

2. **Cache Performance**:
   - Cache hit rate
   - Cache miss rate
   - Cache size

3. **Database Performance**:
   - Query execution time
   - Database file size
   - Read/write operations

4. **System Resources**:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Disk space

#### Log Analysis

```bash
# Analyze slow requests
grep "Slow Request" logs/performance.log | tail -20

# Analyze cache performance
grep "Cache Hit" logs/performance.log | tail -20

# Analyze memory usage
grep "Memory Usage" logs/performance.log | tail -20
```

## Optimization Guidelines

### For Developers

1. **Use Caching**:
   - Cache frequently accessed data
   - Use appropriate TTL values
   - Invalidate cache on updates

2. **Implement Pagination**:
   - Always paginate large datasets
   - Use reasonable page sizes
   - Implement lazy loading for infinite scroll

3. **Optimize Database Queries**:
   - Minimize database reads
   - Use batch operations
   - Cache query results

4. **Optimize Templates**:
   - Avoid complex logic in templates
   - Use template fragments
   - Minimize database queries

5. **Use Async for Long Operations**:
   - Implement background tasks for long operations
   - Use async I/O for database operations
   - Queue non-critical operations

6. **Monitor Performance**:
   - Log slow operations
   - Track performance metrics
   - Set up monitoring alerts

### For Administrators

1. **Monitor Performance**:
   - Review performance logs regularly
   - Monitor system resources
   - Track cache hit rates

2. **Optimize Infrastructure**:
   - Use SSD storage
   - Ensure adequate RAM
   - Monitor CPU usage

3. **Scale as Needed**:
   - Implement horizontal scaling
   - Use load balancers
   - Consider caching layers (Redis)

4. **Regular Maintenance**:
   - Clean up old logs
   - Rotate cache
   - Update dependencies

## Performance Tuning

### Memory Tuning

```python
# Increase cache timeout for better hit rates
CACHE_DEFAULT_TIMEOUT=7200  # 2 hours

# Increase template cache
TEMPLATE_CACHE_TIMEOUT=7200
```

### Database Tuning

```python
# Use smaller page sizes for better performance
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=50
```

### Cache Tuning

```python
# Adjust cache TTL based on data update frequency
CACHE_DEPARTMENT_TIMEOUT=1800  # 30 minutes for frequently updated data
CACHE_MEDICINE_TIMEOUT=3600   # 1 hour for less frequently updated data
```

## Scalability Considerations

### Current Architecture

- Single-node application
- File-based database
- In-memory caching
- Local file storage

### Scaling Options

1. **Vertical Scaling**:
   - Increase RAM for better caching
   - Use faster SSD storage
   - Increase CPU for better processing

2. **Horizontal Scaling**:
   - Load balancer + multiple app instances
   - Shared session storage (Redis)
   - Shared cache (Redis)
   - Shared file storage (S3, NFS)

3. **Database Scaling**:
   - Migrate from JSON files to PostgreSQL/MySQL
   - Implement database connection pooling
   - Use read replicas

4. **Caching Scaling**:
   - Replace in-memory cache with Redis
   - Implement cache clustering
   - Use distributed cache

## Monitoring and Alerting

### Setup Monitoring

1. **Log Monitoring**:
   - Centralized log collection (ELK stack)
   - Log rotation and retention
   - Error rate monitoring

2. **Performance Monitoring**:
   - APM tool (New Relic, Datadog)
   - Custom metrics collection
   - Dashboard for key metrics

3. **Infrastructure Monitoring**:
   - System resource monitoring
   - Database performance monitoring
   - Network monitoring

### Alert Thresholds

```yaml
alerts:
  - metric: response_time_p95
    threshold: 3 seconds
    severity: warning

  - metric: cache_hit_rate
    threshold: < 70%
    severity: critical

  - metric: memory_usage
    threshold: > 85%
    severity: warning

  - metric: disk_usage
    threshold: > 90%
    severity: critical
```

## Changelog

### Version 1.0.0 (Phase 7)
- Implemented caching system
- Added pagination support
- Implemented performance monitoring
- Added health check endpoints
- Created performance tests
- Added slow operation detection
- Implemented cache invalidation
- Added performance logging
- Created performance documentation
