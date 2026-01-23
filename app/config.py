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

    # =============================================================================
    # SECURITY
    # =============================================================================

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'

    # Password Policy
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', '8'))
    PASSWORD_REQUIRE_UPPERCASE = os.environ.get('PASSWORD_REQUIRE_UPPERCASE', 'True') == 'True'
    PASSWORD_REQUIRE_LOWERCASE = os.environ.get('PASSWORD_REQUIRE_LOWERCASE', 'True') == 'True'
    PASSWORD_REQUIRE_DIGITS = os.environ.get('PASSWORD_REQUIRE_DIGITS', 'True') == 'True'
    PASSWORD_REQUIRE_SPECIAL = os.environ.get('PASSWORD_REQUIRE_SPECIAL', 'True') == 'True'

    # Account Lockout
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
    ACCOUNT_LOCKOUT_DURATION = timedelta(minutes=int(os.environ.get('ACCOUNT_LOCKOUT_DURATION', '30')))

    # =============================================================================
    # SESSION CONFIGURATION
    # =============================================================================

    SESSION_TYPE = os.environ.get('SESSION_TYPE', 'filesystem')
    SESSION_PERMANENT = os.environ.get('SESSION_PERMANENT', 'False') == 'True'
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', '86400')))
    SESSION_USE_SIGNER = os.environ.get('SESSION_USE_SIGNER', 'True') == 'True'
    SESSION_KEY_PREFIX = os.environ.get('SESSION_KEY_PREFIX', 'pharmacy:')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True') == 'True'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')

    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================

    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    PORT = int(os.environ.get('PORT', '5045'))
    ENV = os.environ.get('FLASK_ENV', 'development')

    # =============================================================================
    # FILE SYSTEM PATHS
    # =============================================================================

    DATA_DIR = os.environ.get('DATA_DIR', 'data')
    BACKUP_DIR = os.environ.get('BACKUP_DIR', 'backups')
    UPLOAD_DIR = os.environ.get('UPLOAD_DIR', 'uploads')
    LOG_DIR = os.environ.get('LOG_DIR', 'logs')
    FLASK_SESSION_DIR = os.environ.get('FLASK_SESSION_DIR', 'flask_session')

    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================

    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True') == 'True'
    WTF_CSRF_TIME_LIMIT = None

    # Security Headers
    SECURITY_HEADERS_ENABLED = os.environ.get('SECURITY_HEADERS_ENABLED', 'True') == 'True'

    # =============================================================================
    # BACKUP SETTINGS
    # =============================================================================

    AUTO_BACKUP_ENABLED = os.environ.get('AUTO_BACKUP_ENABLED', 'False') == 'True'
    BACKUP_SCHEDULE = os.environ.get('BACKUP_SCHEDULE', 'daily')
    MAX_BACKUP_FILES = int(os.environ.get('MAX_BACKUP_FILES', '30'))

    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================

    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # =============================================================================
    # RATE LIMITING
    # =============================================================================

    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/hour')
    LOGIN_RATE_LIMIT = os.environ.get('LOGIN_RATE_LIMIT', '5/15m')
    UPLOAD_RATE_LIMIT = os.environ.get('UPLOAD_RATE_LIMIT', '10/m')

    # =============================================================================
    # AI/CHATBOT CONFIGURATION
    # =============================================================================

    # OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

    # OpenRouter
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

    # Google AI
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

    # Chatbot Settings
    CHATBOT_ENABLED = os.environ.get('CHATBOT_ENABLED', 'False') == 'True'
    CHATBOT_PROVIDER = os.environ.get('CHATBOT_PROVIDER', 'openai')
    CHATBOT_MODEL = os.environ.get('CHATBOT_MODEL', 'gpt-4')
    CHATBOT_MAX_TOKENS = int(os.environ.get('CHATBOT_MAX_TOKENS', '1000'))
    CHATBOT_TEMPERATURE = float(os.environ.get('CHATBOT_TEMPERATURE', '0.7'))

    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================

    # PostgreSQL/SQLite URL (for future migration from JSON)
    DATABASE_URL = os.environ.get('DATABASE_URL', '')

    # =============================================================================
    # CACHE CONFIGURATION
    # =============================================================================

    REDIS_URL = os.environ.get('REDIS_URL', '')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '3600'))
    CACHE_DEPARTMENT_TIMEOUT = int(os.environ.get('CACHE_DEPARTMENT_TIMEOUT', '3600'))
    CACHE_SUPPLIER_TIMEOUT = int(os.environ.get('CACHE_SUPPLIER_TIMEOUT', '3600'))
    CACHE_MEDICINE_TIMEOUT = int(os.environ.get('CACHE_MEDICINE_TIMEOUT', '3600'))

    # =============================================================================
    # EMAIL CONFIGURATION
    # =============================================================================

    MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')

    # =============================================================================
    # EXTERNAL SERVICES
    # =============================================================================

    SENTRY_DSN = os.environ.get('SENTRY_DSN', '')

    # AWS S3
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET', '')
    AWS_S3_REGION = os.environ.get('AWS_S3_REGION', 'us-east-1')

    # =============================================================================
    # PERFORMANCE SETTINGS
    # =============================================================================

    DEFAULT_PAGE_SIZE = int(os.environ.get('DEFAULT_PAGE_SIZE', '25'))
    MAX_PAGE_SIZE = int(os.environ.get('MAX_PAGE_SIZE', '100'))
    DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', '10'))
    DB_POOL_TIMEOUT = int(os.environ.get('DB_POOL_TIMEOUT', '30'))
    DB_POOL_RECYCLE = int(os.environ.get('DB_POOL_RECYCLE', '3600'))
    TEMPLATE_CACHE_TIMEOUT = int(os.environ.get('TEMPLATE_CACHE_TIMEOUT', '3600'))

    # =============================================================================
    # DEVELOPMENT/TESTING
    # =============================================================================

    DEV_SERVER_RELOAD = os.environ.get('DEV_SERVER_RELOAD', 'False') == 'True'
    DEV_SERVER_AUTO_RELOAD = os.environ.get('DEV_SERVER_AUTO_RELOAD', 'True') == 'True'

    # =============================================================================
    # SSL/TLS
    # =============================================================================

    SSL_DISABLE = os.environ.get('SSL_DISABLE', 'False') == 'True'
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH', '')
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', '')

    # =============================================================================
    # REVERSE PROXY
    # =============================================================================

    TRUST_PROXY_HEADERS = os.environ.get('TRUST_PROXY_HEADERS', 'False') == 'True'
    TRUST_PROXY_IPS = os.environ.get('TRUST_PROXY_IPS', '')

    # Legacy API key header (for backward compatibility)
    API_KEY_HEADER = 'X-API-Key'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    # Ensure cookies work on localhost (HTTP)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'

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