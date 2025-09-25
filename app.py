"""
Hospital Pharmacy Management System
Main Flask Application Entry Point
"""

from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
import os
from datetime import datetime

# Import blueprints
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.medicines import medicines_bp
from blueprints.patients import patients_bp
from blueprints.doctors import doctors_bp
from blueprints.suppliers import suppliers_bp
from blueprints.departments import departments_bp
from blueprints.stores import stores_bp
from blueprints.purchases import purchases_bp
from blueprints.consumption import consumption_bp
from blueprints.reports import reports_bp
from blueprints.settings import settings_bp
from blueprints.chatbot import chatbot_bp
from blueprints.transfers import transfers_bp
from blueprints.photos import photos_bp

# Import utilities
from utils.database import init_database
from utils.helpers import login_required

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'hospital-pharmacy-secret-key-2024'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    
    # Initialize session
    Session(app)
    
    # Initialize database
    init_database()
    
    # Register blueprints
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
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
    app.register_blueprint(transfers_bp, url_prefix='/transfers')
    app.register_blueprint(photos_bp, url_prefix='/photos')

    # Root route
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500
    
    # Template globals
    @app.template_global()
    def current_year():
        return datetime.now().year
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5045)
