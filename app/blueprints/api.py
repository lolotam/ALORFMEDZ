"""
API Blueprint for Hospital Pharmacy Management System
Provides REST API endpoints for external integrations
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from functools import wraps
import os

# Import utilities
from app.utils.database import get_medicines, get_stores
from app.utils.chatbot_database import chatbot_db

api_bp = Blueprint('api', __name__)

# API Key for authentication
API_KEY = os.environ.get('API_KEY', 'pharmacy-api-key-2024')


def api_key_required(f):
    """Decorator to require API key for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key_header = request.headers.get('X-API-Key')
        if api_key_header != API_KEY:
            return jsonify({
                'success': False,
                'error': 'Invalid or missing API key'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/webhook/inventory-alert', methods=['POST'])
@api_key_required
def webhook_inventory_alert():
    """Webhook for n8n to trigger inventory alerts"""
    try:
        # Get low stock medicines
        low_stock = chatbot_db.get_advanced_analytics('low_stock_analysis')

        # Format for n8n processing
        alert_data = {
            'alert_type': 'low_stock',
            'medicines': low_stock.get('medicines', []),
            'count': len(low_stock.get('medicines', [])),
            'timestamp': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'data': alert_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/medicines', methods=['GET'])
@api_key_required
def get_medicines_api():
    """Get all medicines"""
    try:
        medicines = get_medicines()
        return jsonify({
            'success': True,
            'data': medicines,
            'count': len(medicines)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/inventory/low-stock', methods=['GET'])
@api_key_required
def get_low_stock_api():
    """Get medicines with low stock"""
    try:
        medicines = get_medicines()
        low_stock = [
            m for m in medicines
            if m.get('quantity', 0) < m.get('low_stock_limit', 10)
        ]
        return jsonify({
            'success': True,
            'data': low_stock,
            'count': len(low_stock)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint - no authentication required"""
    return jsonify({
        'status': 'healthy',
        'service': 'ALORF Hospital Pharmacy API',
        'timestamp': datetime.now().isoformat()
    })
