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