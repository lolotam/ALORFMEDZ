"""
Production Configuration for Hospital Pharmacy Management System
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'

    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'pharmacy:'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Application Settings
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload

    # Database
    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    BACKUP_DIR = os.environ.get('BACKUP_DIR', 'backups')
    UPLOAD_DIR = os.environ.get('UPLOAD_DIR', 'uploads')

    # Security Settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # Password Policy
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    MAX_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_DURATION = timedelta(minutes=30)

    # Backup Settings
    AUTO_BACKUP_ENABLED = os.environ.get('AUTO_BACKUP_ENABLED', 'False') == 'True'
    BACKUP_SCHEDULE = os.environ.get('BACKUP_SCHEDULE', 'daily')  # daily, weekly, monthly
    MAX_BACKUP_FILES = int(os.environ.get('MAX_BACKUP_FILES', '30'))

    # Logging
    LOG_DIR = os.environ.get('LOG_DIR', 'logs')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # API Settings
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/hour')
    API_KEY_HEADER = 'X-API-Key'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    ENV = 'production'

    # Enforce security in production
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True

    # Production-specific settings
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files
    PREFERRED_URL_SCHEME = 'https'

    # Enhanced security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'"
    }

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    ENV = 'testing'
    WTF_CSRF_ENABLED = False

    # Use temporary database for tests
    DATA_DIR = 'test_data'
    BACKUP_DIR = 'test_backups'
    UPLOAD_DIR = 'test_uploads'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration object based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, DevelopmentConfig)