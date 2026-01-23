"""
WSGI Entry Point for Production Deployment

This file is used by WSGI servers like Gunicorn to serve the application.
Example: gunicorn -w 4 -b 0.0.0.0:5045 wsgi:application
"""

import os
from app import create_app

# Get configuration from environment
config_name = os.environ.get('FLASK_ENV', 'production')

# Create application instance
application = create_app(config_name)

if __name__ == "__main__":
    # For development only - use wsgi server in production
    application.run()
