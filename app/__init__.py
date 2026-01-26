"""
Hospital Pharmacy Management System
Main Application Package - Application Factory
"""

from flask import Flask, render_template, session, redirect, url_for, send_from_directory, jsonify, request
from flask_session import Session
import os
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix

# Import configuration
from .config import get_config

# Import blueprints (from new locations within app package)
from .blueprints.auth import auth_bp
from .blueprints.dashboard import dashboard_bp
from .blueprints.medicines import medicines_bp
from .blueprints.patients import patients_bp
from .blueprints.doctors import doctors_bp
from .blueprints.suppliers import suppliers_bp
from .blueprints.departments import departments_bp
from .blueprints.stores import stores_bp
from .blueprints.purchases import purchases_bp
from .blueprints.consumption import consumption_bp
from .blueprints.reports import reports_bp
# New refactored blueprints
from .blueprints.settings import settings_bp
from .blueprints.users import users_bp
from .blueprints.backup import backup_bp
from .blueprints.security import security_bp
# Chatbot package with config routes
from .blueprints.chatbot import chatbot_bp, chatbot_config_bp
from .blueprints.transfers import transfers_bp
from .blueprints.photos import photos_bp
from .blueprints.api import api_bp
# Health check blueprint
from .blueprints.health import health_bp

# Import utilities
from .utils.database import init_database
from .utils.upload import ensure_upload_directory
from .utils.logging_config import setup_logging
from .utils.middleware import setup_middleware
from .utils.cache import get_cache
from .utils.csrf import require_csrf_token, get_csrf_token_for_ajax


def create_app(config_name=None):
    """Application factory pattern

    Args:
        config_name: Configuration name ('development', 'production', 'testing')

    Returns:
        Configured Flask application
    """
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Fix for mixed content issues (HTTPS proxy)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize logging
    setup_logging(app)

    # Initialize session
    Session(app)

    # Initialize database
    init_database()

    # Initialize upload directories
    ensure_upload_directory()

    # Setup middleware
    setup_middleware(app)

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix='/health')  # Register health check first
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(medicines_bp, url_prefix='/medicines')
    app.register_blueprint(patients_bp, url_prefix='/patients')
    app.register_blueprint(doctors_bp, url_prefix='/doctors')
    app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
    app.register_blueprint(departments_bp, url_prefix='/departments')
    app.register_blueprint(stores_bp, url_prefix='/stores')
    app.register_blueprint(purchases_bp, url_prefix='/purchases')
    app.register_blueprint(consumption_bp, url_prefix='/consumption')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    # New refactored blueprints
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(backup_bp, url_prefix='/backup')
    app.register_blueprint(security_bp, url_prefix='/security')
    # Chatbot blueprints (main + config)
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(chatbot_config_bp, url_prefix='/chatbot')
    app.register_blueprint(transfers_bp, url_prefix='/transfers')
    app.register_blueprint(photos_bp, url_prefix='/photos')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Root route
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # CSRF token endpoint for AJAX requests
    @app.route('/csrf-token')
    def csrf_token():
        """Get CSRF token for AJAX requests"""
        require_csrf_token()
        token_info = get_csrf_token_for_ajax()
        return jsonify(token_info)

    # Favicon route
    @app.route('/favicon/<path:filename>')
    def favicon(filename):
        """Serve favicon files"""
        return send_from_directory('../favicon', filename)

    # Error handlers (consolidated - no duplicates)
    @app.errorhandler(404)
    def not_found_error(error):
        # Don't log 404 errors to avoid spam
        try:
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Not found',
                    'message': 'The requested resource was not found'
                }), 404
        except RuntimeError:
            # Request context not available
            pass
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        try:
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Internal server error',
                    'message': 'An unexpected error occurred. Please try again later.'
                }), 500
        except RuntimeError:
            # Request context not available
            pass
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        try:
            app.logger.warning(f"Forbidden access attempt: {request.url}")
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': 'You do not have permission to access this resource'
                }), 403
        except RuntimeError:
            # Request context not available
            pass
        return render_template('errors/403.html'), 403

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        try:
            app.logger.warning(f"Rate limit exceeded for {request.url}")
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.'
                }), 429
        except RuntimeError:
            # Request context not available
            pass
        return jsonify({
            'success': False,
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.'
        }), 429

    # Template globals
    @app.template_global()
    def current_year():
        return datetime.now().year

    @app.template_global()
    def get_csrf_token():
        """Get CSRF token for templates"""
        from .utils.csrf import get_csrf_token as _get_csrf_token
        return _get_csrf_token()

    # Template filters
    @app.template_filter('format_bytes')
    def format_bytes(bytes_value):
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"

    # Initialize cache cleanup on first request
    @app.before_request
    def initialize_cache():
        """Initialize cache cleanup on first request"""
        if not hasattr(app, '_cache_initialized'):
            cache = get_cache()
            cache.cleanup()
            app._cache_initialized = True

    app.logger.info("Application initialized successfully")

    return app
