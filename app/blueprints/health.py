"""
Health Check Blueprint

Provides endpoints for monitoring application health and status.
"""

import os
import time
import psutil
from flask import Blueprint, jsonify
from app.utils.database import init_database
from app.utils.logging_config import security_logger, performance_logger

health_bp = Blueprint('health', __name__)


@health_bp.route('/health')
def health_check():
    """
    Health check endpoint for monitoring systems.

    Returns:
        JSON response with application status
    """
    try:
        # Check database
        db_status = check_database()

        # Check file system
        fs_status = check_file_system()

        # Check memory
        memory_status = check_memory()

        # Check disk space
        disk_status = check_disk_space()

        # Overall status
        all_healthy = all([
            db_status['status'] == 'healthy',
            fs_status['status'] == 'healthy',
            memory_status['status'] == 'healthy',
            disk_status['status'] == 'healthy'
        ])

        response = {
            'status': 'healthy' if all_healthy else 'degraded',
            'timestamp': time.time(),
            'checks': {
                'database': db_status,
                'file_system': fs_status,
                'memory': memory_status,
                'disk': disk_status
            },
            'version': '1.0.0',
            'uptime': get_uptime()
        }

        status_code = 200 if all_healthy else 503
        return jsonify(response), status_code

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500


@health_bp.route('/health/ready')
def readiness_check():
    """
    Readiness probe endpoint.

    Returns:
        JSON response indicating if app is ready to serve traffic
    """
    try:
        # Check if database is accessible
        db_status = check_database()

        if db_status['status'] != 'healthy':
            return jsonify({
                'status': 'not_ready',
                'reason': 'Database not accessible'
            }), 503

        return jsonify({
            'status': 'ready',
            'timestamp': time.time()
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'error': str(e)
        }), 503


@health_bp.route('/health/live')
def liveness_check():
    """
    Liveness probe endpoint.

    Returns:
        JSON response indicating if app is alive
    """
    return jsonify({
        'status': 'alive',
        'timestamp': time.time()
    }), 200


@health_bp.route('/health/metrics')
def metrics():
    """
    Metrics endpoint for monitoring systems.

    Returns:
        JSON response with application metrics
    """
    try:
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')

        return jsonify({
            'timestamp': time.time(),
            'metrics': {
                'memory': {
                    'total': memory_info.total,
                    'available': memory_info.available,
                    'used': memory_info.used,
                    'percentage': memory_info.percent
                },
                'disk': {
                    'total': disk_info.total,
                    'used': disk_info.used,
                    'free': disk_info.free,
                    'percentage': (disk_info.used / disk_info.total) * 100
                },
                'cpu': {
                    'count': psutil.cpu_count(),
                    'usage': psutil.cpu_percent(interval=1)
                },
                'uptime': get_uptime()
            }
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


def check_database():
    """Check database connectivity"""
    try:
        # Try to initialize database (lightweight check)
        start_time = time.time()
        init_database()
        response_time = time.time() - start_time

        return {
            'status': 'healthy',
            'response_time': response_time
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def check_file_system():
    """Check file system access"""
    try:
        # Check if required directories exist
        required_dirs = ['data', 'uploads', 'backups']
        for directory in required_dirs:
            if not os.path.exists(directory):
                return {
                    'status': 'degraded',
                    'message': f'Directory {directory} does not exist'
                }

        # Check write permissions
        test_file = 'data/health_check.tmp'
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)

            return {
                'status': 'healthy'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': f'Write permission error: {str(e)}'
            }

    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def check_memory():
    """Check memory usage"""
    try:
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        if memory_percent > 90:
            status = 'unhealthy'
        elif memory_percent > 80:
            status = 'degraded'
        else:
            status = 'healthy'

        return {
            'status': status,
            'usage_percent': memory_percent,
            'available_gb': round(memory.available / (1024**3), 2),
            'total_gb': round(memory.total / (1024**3), 2)
        }

    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def check_disk_space():
    """Check disk space"""
    try:
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100

        if disk_percent > 95:
            status = 'unhealthy'
        elif disk_percent > 85:
            status = 'degraded'
        else:
            status = 'healthy'

        return {
            'status': status,
            'usage_percent': round(disk_percent, 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'total_gb': round(disk.total / (1024**3), 2)
        }

    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def get_uptime():
    """Get application uptime"""
    try:
        boot_time = psutil.boot_time()
        now = time.time()
        uptime_seconds = now - boot_time

        # Convert to hours, minutes, seconds
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        return {
            'seconds': int(uptime_seconds),
            'readable': f"{hours}h {minutes}m {seconds}s",
            'boot_time': boot_time
        }

    except Exception as e:
        return {
            'error': str(e)
        }
