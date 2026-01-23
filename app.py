"""
Hospital Pharmacy Management System
Main Flask Application Entry Point

This is a thin wrapper that imports from the app package.
The main application factory is located in app/__init__.py
"""

if __name__ == '__main__':
    from app import create_app

    # Create application instance using environment config
    import os
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)

    # Run development server
    app.run(
        debug=True,
        host='0.0.0.0',
        port=app.config.get('PORT', 5045)
    )
