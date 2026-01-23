"""
Performance Monitoring and Metrics System
Real-time performance tracking for the Hospital Pharmacy Management System
"""

import time
import psutil
import threading
import json
import os
from collections import deque, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from functools import wraps
from flask import request, g, current_app
import weakref

class MetricsCollector:
    """Thread-safe metrics collection with circular buffers"""

    def __init__(self, max_history=1000):
        self.max_history = max_history
        self.request_metrics = deque(maxlen=max_history)
        self.database_metrics = deque(maxlen=max_history)
        self.cache_metrics = deque(maxlen=max_history)
        self.system_metrics = deque(maxlen=max_history)
        self.error_metrics = deque(maxlen=max_history)
        self.lock = threading.RLock()

        # Aggregated stats
        self.request_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'errors': 0})
        self.endpoint_stats = defaultdict(lambda: {'count': 0, 'avg_time': 0, 'max_time': 0})

    def record_request(self, endpoint: str, method: str, duration: float,
                      status_code: int, memory_usage: int = 0):
        """Record HTTP request metrics"""
        with self.lock:
            metric = {
                'timestamp': time.time(),
                'endpoint': endpoint,
                'method': method,
                'duration': duration,
                'status_code': status_code,
                'memory_usage': memory_usage,
                'user_id': getattr(g, 'user_id', None)
            }

            self.request_metrics.append(metric)

            # Update aggregated stats
            key = f"{method}:{endpoint}"
            self.request_stats[key]['count'] += 1
            self.request_stats[key]['total_time'] += duration

            if status_code >= 400:
                self.request_stats[key]['errors'] += 1

            # Update endpoint stats
            endpoint_stat = self.endpoint_stats[endpoint]
            endpoint_stat['count'] += 1
            endpoint_stat['max_time'] = max(endpoint_stat['max_time'], duration)
            endpoint_stat['avg_time'] = (
                (endpoint_stat['avg_time'] * (endpoint_stat['count'] - 1) + duration)
                / endpoint_stat['count']
            )

    def record_database_operation(self, operation: str, table: str, duration: float,
                                cache_hit: bool = False, record_count: int = 0):
        """Record database operation metrics"""
        with self.lock:
            metric = {
                'timestamp': time.time(),
                'operation': operation,
                'table': table,
                'duration': duration,
                'cache_hit': cache_hit,
                'record_count': record_count
            }
            self.database_metrics.append(metric)

    def record_cache_operation(self, operation: str, key: str, hit: bool, duration: float = 0):
        """Record cache operation metrics"""
        with self.lock:
            metric = {
                'timestamp': time.time(),
                'operation': operation,
                'key': key,
                'hit': hit,
                'duration': duration
            }
            self.cache_metrics.append(metric)

    def record_system_metrics(self):
        """Record current system metrics"""
        try:
            process = psutil.Process()

            metric = {
                'timestamp': time.time(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_rss': process.memory_info().rss,
                'memory_vms': process.memory_info().vms,
                'open_files': len(process.open_files()),
                'threads': process.num_threads(),
                'system_cpu': psutil.cpu_percent(interval=None),
                'system_memory': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }

            with self.lock:
                self.system_metrics.append(metric)

        except Exception as e:
            print(f"Error collecting system metrics: {e}")

    def record_error(self, error_type: str, message: str, endpoint: str = None,
                    traceback: str = None):
        """Record application error"""
        with self.lock:
            metric = {
                'timestamp': time.time(),
                'error_type': error_type,
                'message': message,
                'endpoint': endpoint,
                'traceback': traceback,
                'user_id': getattr(g, 'user_id', None)
            }
            self.error_metrics.append(metric)

    def get_summary_stats(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get summary statistics for the specified time window (seconds)"""
        cutoff_time = time.time() - time_window

        with self.lock:
            # Filter recent metrics
            recent_requests = [m for m in self.request_metrics if m['timestamp'] > cutoff_time]
            recent_db_ops = [m for m in self.database_metrics if m['timestamp'] > cutoff_time]
            recent_errors = [m for m in self.error_metrics if m['timestamp'] > cutoff_time]

            # Calculate stats
            if recent_requests:
                avg_response_time = sum(m['duration'] for m in recent_requests) / len(recent_requests)
                max_response_time = max(m['duration'] for m in recent_requests)
                error_rate = len([m for m in recent_requests if m['status_code'] >= 400]) / len(recent_requests)
            else:
                avg_response_time = max_response_time = error_rate = 0

            if recent_db_ops:
                cache_hit_rate = len([m for m in recent_db_ops if m['cache_hit']]) / len(recent_db_ops)
                avg_db_time = sum(m['duration'] for m in recent_db_ops) / len(recent_db_ops)
            else:
                cache_hit_rate = avg_db_time = 0

            return {
                'time_window': time_window,
                'requests': {
                    'total': len(recent_requests),
                    'avg_response_time': avg_response_time,
                    'max_response_time': max_response_time,
                    'error_rate': error_rate,
                    'requests_per_second': len(recent_requests) / time_window if time_window > 0 else 0
                },
                'database': {
                    'total_operations': len(recent_db_ops),
                    'cache_hit_rate': cache_hit_rate,
                    'avg_operation_time': avg_db_time
                },
                'errors': {
                    'total': len(recent_errors),
                    'error_rate': len(recent_errors) / time_window if time_window > 0 else 0
                }
            }

    def get_slow_endpoints(self, threshold: float = 1.0, limit: int = 10) -> List[Dict]:
        """Get endpoints with response times above threshold"""
        with self.lock:
            slow_endpoints = []
            for endpoint, stats in self.endpoint_stats.items():
                if stats['avg_time'] > threshold:
                    slow_endpoints.append({
                        'endpoint': endpoint,
                        'avg_time': stats['avg_time'],
                        'max_time': stats['max_time'],
                        'count': stats['count']
                    })

            return sorted(slow_endpoints, key=lambda x: x['avg_time'], reverse=True)[:limit]

# Global metrics collector
metrics = MetricsCollector()

class PerformanceMonitor:
    """Flask performance monitoring middleware"""

    def __init__(self, app=None):
        self.app = app
        self.system_monitor_thread = None
        self.monitoring_active = False

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize performance monitoring for Flask app"""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_appcontext(self._teardown_request)

        # Start system monitoring thread
        self.start_system_monitoring()

        # Register cleanup
        import atexit
        atexit.register(self.stop_system_monitoring)

    def _before_request(self):
        """Record request start time and memory"""
        g.start_time = time.time()
        g.start_memory = self._get_memory_usage()

    def _after_request(self, response):
        """Record request completion metrics"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            memory_diff = self._get_memory_usage() - getattr(g, 'start_memory', 0)

            metrics.record_request(
                endpoint=request.endpoint or request.path,
                method=request.method,
                duration=duration,
                status_code=response.status_code,
                memory_usage=memory_diff
            )

        return response

    def _teardown_request(self, exception):
        """Handle request errors"""
        if exception:
            metrics.record_error(
                error_type=type(exception).__name__,
                message=str(exception),
                endpoint=request.endpoint or request.path,
                traceback=None  # Could add full traceback if needed
            )

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except:
            return 0

    def start_system_monitoring(self):
        """Start background system monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True

        def monitor_loop():
            while self.monitoring_active:
                metrics.record_system_metrics()
                time.sleep(30)  # Record every 30 seconds

        self.system_monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.system_monitor_thread.start()

    def stop_system_monitoring(self):
        """Stop background system monitoring"""
        self.monitoring_active = False
        if self.system_monitor_thread:
            self.system_monitor_thread.join(timeout=1)

def performance_tracker(operation_type: str = 'function'):
    """Decorator to track function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Record different types of operations
                if operation_type == 'database':
                    table = kwargs.get('file_type', 'unknown')
                    cache_hit = kwargs.get('cache_hit', False)
                    record_count = len(result) if isinstance(result, list) else 1

                    metrics.record_database_operation(
                        operation=func.__name__,
                        table=table,
                        duration=duration,
                        cache_hit=cache_hit,
                        record_count=record_count
                    )

                return result

            except Exception as e:
                duration = time.time() - start_time
                metrics.record_error(
                    error_type=type(e).__name__,
                    message=str(e)
                )
                raise

        return wrapper
    return decorator

class AlertSystem:
    """Performance alerting system"""

    def __init__(self):
        self.thresholds = {
            'avg_response_time': 2.0,  # seconds
            'error_rate': 0.05,        # 5%
            'memory_usage': 80.0,      # 80%
            'cpu_usage': 80.0,         # 80%
            'cache_hit_rate': 0.70     # 70%
        }
        self.alert_cooldown = {}
        self.cooldown_period = 300  # 5 minutes

    def check_alerts(self) -> List[Dict]:
        """Check for performance issues and return alerts"""
        alerts = []
        current_time = time.time()
        stats = metrics.get_summary_stats(time_window=300)  # 5 minutes

        # Check response time
        if stats['requests']['avg_response_time'] > self.thresholds['avg_response_time']:
            alert_key = 'slow_response'
            if self._should_alert(alert_key, current_time):
                alerts.append({
                    'type': 'performance',
                    'severity': 'warning',
                    'message': f"Average response time is {stats['requests']['avg_response_time']:.2f}s",
                    'metric': 'avg_response_time',
                    'value': stats['requests']['avg_response_time'],
                    'threshold': self.thresholds['avg_response_time']
                })

        # Check error rate
        if stats['requests']['error_rate'] > self.thresholds['error_rate']:
            alert_key = 'high_error_rate'
            if self._should_alert(alert_key, current_time):
                alerts.append({
                    'type': 'error',
                    'severity': 'critical',
                    'message': f"Error rate is {stats['requests']['error_rate']:.1%}",
                    'metric': 'error_rate',
                    'value': stats['requests']['error_rate'],
                    'threshold': self.thresholds['error_rate']
                })

        # Check cache hit rate
        if stats['database']['cache_hit_rate'] < self.thresholds['cache_hit_rate']:
            alert_key = 'low_cache_hit'
            if self._should_alert(alert_key, current_time):
                alerts.append({
                    'type': 'performance',
                    'severity': 'warning',
                    'message': f"Cache hit rate is {stats['database']['cache_hit_rate']:.1%}",
                    'metric': 'cache_hit_rate',
                    'value': stats['database']['cache_hit_rate'],
                    'threshold': self.thresholds['cache_hit_rate']
                })

        return alerts

    def _should_alert(self, alert_key: str, current_time: float) -> bool:
        """Check if enough time has passed since last alert"""
        last_alert_time = self.alert_cooldown.get(alert_key, 0)
        if current_time - last_alert_time > self.cooldown_period:
            self.alert_cooldown[alert_key] = current_time
            return True
        return False

class PerformanceReport:
    """Generate performance reports"""

    @staticmethod
    def generate_daily_report() -> Dict[str, Any]:
        """Generate comprehensive daily performance report"""
        stats_24h = metrics.get_summary_stats(time_window=86400)  # 24 hours
        stats_1h = metrics.get_summary_stats(time_window=3600)    # 1 hour

        slow_endpoints = metrics.get_slow_endpoints(threshold=1.0, limit=10)

        return {
            'report_date': datetime.now().isoformat(),
            'summary': {
                '24_hour': stats_24h,
                '1_hour': stats_1h
            },
            'slow_endpoints': slow_endpoints,
            'recommendations': PerformanceReport._generate_recommendations(stats_24h, slow_endpoints)
        }

    @staticmethod
    def _generate_recommendations(stats: Dict, slow_endpoints: List[Dict]) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        if stats['requests']['avg_response_time'] > 1.0:
            recommendations.append("Consider implementing response caching for frequently accessed data")

        if stats['database']['cache_hit_rate'] < 0.7:
            recommendations.append("Increase cache TTL or optimize cache invalidation strategy")

        if len(slow_endpoints) > 5:
            recommendations.append("Optimize database queries for slow endpoints")

        if stats['requests']['error_rate'] > 0.02:
            recommendations.append("Investigate and fix sources of application errors")

        return recommendations

    @staticmethod
    def export_metrics_to_json(filename: str, time_window: int = 3600):
        """Export metrics to JSON file"""
        cutoff_time = time.time() - time_window

        with metrics.lock:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'time_window': time_window,
                'requests': [m for m in metrics.request_metrics if m['timestamp'] > cutoff_time],
                'database': [m for m in metrics.database_metrics if m['timestamp'] > cutoff_time],
                'system': [m for m in metrics.system_metrics if m['timestamp'] > cutoff_time],
                'errors': [m for m in metrics.error_metrics if m['timestamp'] > cutoff_time]
            }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

# Global instances
performance_monitor = PerformanceMonitor()
alert_system = AlertSystem()

# Convenience function for manual monitoring
def get_performance_dashboard() -> Dict[str, Any]:
    """Get comprehensive performance dashboard data"""
    return {
        'current_stats': metrics.get_summary_stats(time_window=3600),
        'slow_endpoints': metrics.get_slow_endpoints(threshold=0.5, limit=5),
        'recent_alerts': alert_system.check_alerts(),
        'cache_stats': {
            'size': len(metrics.cache_metrics),
            'recent_operations': list(metrics.cache_metrics)[-10:] if metrics.cache_metrics else []
        }
    }