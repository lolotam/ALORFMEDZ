"""
AI Chatbot Blueprint (Admin Only) - Enhanced with Comprehensive Database Access and Administrative Capabilities
"""

import json
import os
import re
import requests
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, session
from utils.helpers import login_required, admin_required
from utils.database import (
    get_medicines, get_patients, get_suppliers, get_consumption,
    get_stores, get_purchases, get_departments, log_activity,
    delete_medicine, update_store_inventory
)
from utils.chatbot_database import chatbot_db
from utils.chatbot_agent import pharmacy_agent
from utils.chat_history import chat_history_manager

chatbot_bp = Blueprint('chatbot', __name__)

# Configuration file path
CONFIG_FILE = 'data/chatbot_config.json'

def load_chatbot_config():
    """Load chatbot configuration from file"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass

    # Default configuration
    return {
        'provider': 'openai',
        'openai_api_key': '',
        'openrouter_api_key': '',
        'google_api_key': '',
        'model': 'gpt-4',
        'max_tokens': 1000,
        'temperature': 0.7,
        'enabled': False,
        'available_models': {
            'openai': [
                {'id': 'gpt-4', 'name': 'GPT-4', 'description': 'OpenAI GPT-4 (Legacy)'},
                {'id': 'gpt-4o', 'name': 'ChatGPT-4.0', 'description': 'OpenAI GPT-4 Omni'},
                {'id': 'gpt-4-turbo', 'name': 'ChatGPT-4.1', 'description': 'OpenAI GPT-4 Turbo (Latest)'},
                {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'description': 'OpenAI GPT-3.5 Turbo'}
            ],
            'openrouter': [
                {'id': 'deepseek/deepseek-r1:nitro', 'name': 'DeepSeek R1 (0528)', 'description': 'DeepSeek R1 reasoning model'},
                {'id': 'meta-llama/llama-3.2-3b-instruct:free', 'name': 'Llama 3.2 3B', 'description': 'Meta Llama 3.2 3B (Free)'}
            ],
            'google': [
                {'id': 'gemini-2.5-pro', 'name': 'Gemini 2.5 Pro', 'description': 'Google Gemini 2.5 Pro (Latest)'},
                {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'description': 'Google Gemini 1.5 Pro'}
            ]
        }
    }

def save_chatbot_config(config):
    """Save chatbot configuration to file"""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_pharmacy_context():
    """Get comprehensive pharmacy data for AI context - Enhanced Version"""
    try:
        # Use the enhanced database manager for comprehensive data
        comprehensive_data = chatbot_db.get_comprehensive_data()

        # Extract key metrics for LLM context
        analytics = comprehensive_data.get('analytics', {})
        inventory_summary = comprehensive_data.get('inventory_summary', {})

        context = {
            'total_counts': analytics.get('total_counts', {}),
            'medicine_categories': analytics.get('medicine_categories', {}),
            'recent_consumption_count': analytics.get('recent_consumption_count', 0),
            'recent_purchase_cost': analytics.get('recent_purchase_cost', 0),
            'top_consuming_patients': analytics.get('top_consuming_patients', [])[:3],
            'low_stock_medicines': comprehensive_data.get('low_stock_alerts', [])[:5],
            'highest_stock_medicines': inventory_summary.get('highest_stock_medicines', [])[:5],
            'out_of_stock_count': inventory_summary.get('out_of_stock_medicines', 0),
            'total_medicines_in_stock': inventory_summary.get('total_medicines_in_stock', 0)
        }

        return context
    except Exception as e:
        print(f"Error getting enhanced pharmacy context: {e}")
        return {}

@chatbot_bp.route('/')
@admin_required
def index():
    """AI Chatbot interface"""
    config = load_chatbot_config()
    user_id = session.get('user_id', 'admin')

    # Get or create current session
    current_session_id = session.get('current_chat_session')
    if not current_session_id:
        current_session_id = chat_history_manager.create_new_session(user_id)
        session['current_chat_session'] = current_session_id

    # Get user's chat sessions
    user_sessions = chat_history_manager.get_user_sessions(user_id)

    # Get current session messages
    current_messages = chat_history_manager.get_session_messages(current_session_id)

    return render_template('chatbot/index.html',
                         config=config,
                         user_sessions=user_sessions,
                         current_session_id=current_session_id,
                         current_messages=current_messages)

@chatbot_bp.route('/config', methods=['GET', 'POST'])
@admin_required
def config():
    """Chatbot configuration management"""
    if request.method == 'POST':
        try:
            config_data = {
                'provider': request.form.get('provider', 'openai'),
                'openai_api_key': request.form.get('openai_api_key', ''),
                'openrouter_api_key': request.form.get('openrouter_api_key', ''),
                'google_api_key': request.form.get('google_api_key', ''),
                'model': request.form.get('model', 'gpt-4'),
                'max_tokens': int(request.form.get('max_tokens', 1000)),
                'temperature': float(request.form.get('temperature', 0.7)),
                'enabled': request.form.get('enabled') == 'on',
                'force_llm': request.form.get('force_llm') == 'on',
                'available_models': load_chatbot_config().get('available_models', {})
            }

            if save_chatbot_config(config_data):
                return jsonify({'success': True, 'message': 'Configuration saved successfully!'})
            else:
                return jsonify({'success': False, 'message': 'Failed to save configuration'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'Error: {str(e)}'})

    # GET request - return current config
    config = load_chatbot_config()
    return jsonify(config)

@chatbot_bp.route('/test-connection', methods=['POST'])
@admin_required
def test_connection():
    """Test LLM API connection"""
    try:
        config = load_chatbot_config()
        provider = config.get('provider', 'openai')

        if provider == 'openai':
            api_key = config.get('openai_api_key')
            if not api_key:
                return jsonify({'success': False, 'message': 'OpenAI API key not configured'})

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': config.get('model', 'gpt-4'),
                    'messages': [{'role': 'user', 'content': 'Hello, this is a test.'}],
                    'max_tokens': 10
                },
                timeout=10
            )

            if response.status_code == 200:
                return jsonify({'success': True, 'message': 'OpenAI connection successful!'})
            else:
                return jsonify({'success': False, 'message': f'OpenAI API error: {response.status_code}'})

        elif provider == 'openrouter':
            api_key = config.get('openrouter_api_key')
            if not api_key:
                return jsonify({'success': False, 'message': 'OpenRouter API key not configured'})

            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'meta-llama/llama-3.2-3b-instruct:free',
                    'messages': [{'role': 'user', 'content': 'Hello, this is a test.'}],
                    'max_tokens': 10
                },
                timeout=10
            )

            if response.status_code == 200:
                return jsonify({'success': True, 'message': 'OpenRouter connection successful!'})
            else:
                return jsonify({'success': False, 'message': f'OpenRouter API error: {response.status_code}'})

        elif provider == 'google':
            api_key = config.get('google_api_key')
            if not api_key:
                return jsonify({'success': False, 'message': 'Google API key not configured'})

            # Test Google Gemini API
            response = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}',
                headers={
                    'Content-Type': 'application/json'
                },
                json={
                    'contents': [{
                        'parts': [{'text': 'Hello, this is a test.'}]
                    }],
                    'generationConfig': {
                        'maxOutputTokens': 10
                    }
                },
                timeout=10
            )

            if response.status_code == 200:
                return jsonify({'success': True, 'message': 'Google Gemini connection successful!'})
            else:
                return jsonify({'success': False, 'message': f'Google API error: {response.status_code}'})

        return jsonify({'success': False, 'message': 'Unknown provider'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Connection test failed: {str(e)}'})

# Cache for OpenRouter models (5 minute TTL)
_openrouter_models_cache = {
    'models': [],
    'timestamp': None
}

@chatbot_bp.route('/fetch-openrouter-models', methods=['GET'])
@admin_required
def fetch_openrouter_models():
    """Fetch all available models from OpenRouter API"""
    import time
    
    try:
        config = load_chatbot_config()
        api_key = config.get('openrouter_api_key', '')
        
        # Check cache (5 minute TTL)
        cache_ttl = 300  # 5 minutes
        if (_openrouter_models_cache['timestamp'] and 
            time.time() - _openrouter_models_cache['timestamp'] < cache_ttl and
            _openrouter_models_cache['models']):
            return jsonify({
                'success': True,
                'models': _openrouter_models_cache['models'],
                'count': len(_openrouter_models_cache['models']),
                'cached': True
            })
        
        # Fetch from OpenRouter API
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
            
        response = requests.get(
            'https://openrouter.ai/api/v1/models',
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'message': f'OpenRouter API error: {response.status_code}',
                'models': []
            })
        
        data = response.json()
        models_raw = data.get('data', [])
        
        # Process and structure models for frontend
        models = []
        for model in models_raw:
            model_id = model.get('id', '')
            model_name = model.get('name', model_id)
            
            # Extract provider from model ID (e.g., "openai/gpt-4" -> "OpenAI")
            provider = model_id.split('/')[0].replace('-', ' ').title() if '/' in model_id else 'Other'
            
            # Get pricing info
            pricing = model.get('pricing', {})
            prompt_price = float(pricing.get('prompt', 0)) * 1000000  # Price per 1M tokens
            completion_price = float(pricing.get('completion', 0)) * 1000000
            
            # Get context length
            context_length = model.get('context_length', 0)
            
            # Get modality
            architecture = model.get('architecture', {})
            modality = architecture.get('modality', 'text->text')
            
            models.append({
                'id': model_id,
                'name': model_name,
                'provider': provider,
                'context_length': context_length,
                'prompt_price': round(prompt_price, 4),
                'completion_price': round(completion_price, 4),
                'modality': modality,
                'description': model.get('description', ''),
                'is_free': prompt_price == 0 and completion_price == 0
            })
        
        # Sort by provider, then by name
        models.sort(key=lambda x: (x['provider'].lower(), x['name'].lower()))
        
        # Update cache
        _openrouter_models_cache['models'] = models
        _openrouter_models_cache['timestamp'] = time.time()
        
        return jsonify({
            'success': True,
            'models': models,
            'count': len(models),
            'cached': False
        })
        
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}")
        return jsonify({
            'success': False,
            'message': f'Error fetching models: {str(e)}',
            'models': []
        })

@chatbot_bp.route('/sessions/new', methods=['POST'])
@admin_required
def new_session():
    """Create a new chat session"""
    try:
        user_id = session.get('user_id', 'admin')
        title = request.json.get('title', None)

        session_id = chat_history_manager.create_new_session(user_id, title)
        session['current_chat_session'] = session_id

        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'New chat session created'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating session: {str(e)}'})

@chatbot_bp.route('/sessions/<session_id>/switch', methods=['POST'])
@admin_required
def switch_session(session_id):
    """Switch to a different chat session"""
    try:
        user_id = session.get('user_id', 'admin')

        # Verify session belongs to user
        user_sessions = chat_history_manager.get_user_sessions(user_id)
        if not any(s['id'] == session_id for s in user_sessions):
            return jsonify({'success': False, 'message': 'Session not found'})

        session['current_chat_session'] = session_id
        messages = chat_history_manager.get_session_messages(session_id)

        return jsonify({
            'success': True,
            'session_id': session_id,
            'messages': messages,
            'message': 'Session switched successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error switching session: {str(e)}'})

@chatbot_bp.route('/sessions/<session_id>/delete', methods=['DELETE'])
@admin_required
def delete_session(session_id):
    """Delete a chat session"""
    try:
        user_id = session.get('user_id', 'admin')

        success = chat_history_manager.delete_session(session_id, user_id)
        if success:
            # If deleting current session, create a new one
            if session.get('current_chat_session') == session_id:
                new_session_id = chat_history_manager.create_new_session(user_id)
                session['current_chat_session'] = new_session_id

            return jsonify({'success': True, 'message': 'Session deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete session'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting session: {str(e)}'})

@chatbot_bp.route('/sessions/<session_id>/rename', methods=['POST'])
@admin_required
def rename_session(session_id):
    """Rename a chat session"""
    try:
        user_id = session.get('user_id', 'admin')
        new_title = request.json.get('title', '').strip()

        if not new_title:
            return jsonify({'success': False, 'message': 'Title cannot be empty'})

        success = chat_history_manager.update_session_title(session_id, user_id, new_title)
        if success:
            return jsonify({'success': True, 'message': 'Session renamed successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to rename session'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error renaming session: {str(e)}'})

def call_llm_api(messages, config):
    """Call the configured LLM API"""
    provider = config.get('provider', 'openai')

    if provider == 'openai':
        api_key = config.get('openai_api_key')
        if not api_key:
            raise Exception("OpenAI API key not configured")

        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': config.get('model', 'gpt-4'),
                'messages': messages,
                'max_tokens': config.get('max_tokens', 1000),
                'temperature': config.get('temperature', 0.7)
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

    elif provider == 'openrouter':
        api_key = config.get('openrouter_api_key')
        if not api_key:
            raise Exception("OpenRouter API key not configured")

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': config.get('model', 'meta-llama/llama-3.2-3b-instruct:free'),
                'messages': messages,
                'max_tokens': config.get('max_tokens', 1000),
                'temperature': config.get('temperature', 0.7)
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

    elif provider == 'google':
        api_key = config.get('google_api_key')
        if not api_key:
            raise Exception("Google API key not configured")

        # Convert messages to Google Gemini format
        gemini_contents = []
        for message in messages:
            if message['role'] == 'user':
                gemini_contents.append({
                    'parts': [{'text': message['content']}],
                    'role': 'user'
                })
            elif message['role'] == 'assistant':
                gemini_contents.append({
                    'parts': [{'text': message['content']}],
                    'role': 'model'
                })
            elif message['role'] == 'system':
                # Add system message as first user message
                gemini_contents.insert(0, {
                    'parts': [{'text': f"System: {message['content']}"}],
                    'role': 'user'
                })

        model_name = config.get('model', 'gemini-1.5-pro')
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}',
            headers={
                'Content-Type': 'application/json'
            },
            json={
                'contents': gemini_contents,
                'generationConfig': {
                    'maxOutputTokens': config.get('max_tokens', 1000),
                    'temperature': config.get('temperature', 0.7)
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                raise Exception("No response from Google Gemini API")
        else:
            raise Exception(f"Google API error: {response.status_code} - {response.text}")

    else:
        raise Exception(f"Unknown provider: {provider}")

@chatbot_bp.route('/query', methods=['POST'])
@admin_required
def query():
    """Handle chatbot queries with enhanced AI agent and LLM integration"""
    try:
        user_query = request.json.get('query', '')
        user_id = session.get('user_id', 'admin')

        # Get current session
        current_session_id = session.get('current_chat_session')
        if not current_session_id:
            current_session_id = chat_history_manager.create_new_session(user_id)
            session['current_chat_session'] = current_session_id

        # Save user message to chat history
        chat_history_manager.add_message(current_session_id, user_id, user_query, 'user')

        # Log the query
        log_activity('QUERY', 'chatbot', user_id, {'query': user_query})

        # Load configuration to check preferences
        config = load_chatbot_config()
        force_llm = config.get('force_llm', False)

        # First, try to handle with AI agent for administrative operations (unless forced to use LLM)
        if not force_llm:
            agent_result = pharmacy_agent.process_command(user_query, user_id)

            # If agent handled it successfully, return the result
            if agent_result.get('success'):
                # Save AI response to chat history
                chat_history_manager.add_message(
                    current_session_id, user_id, agent_result['response'], 'ai',
                    {'agent_handled': True, 'data': agent_result.get('data', {})}
                )

                return jsonify({
                    'response': agent_result['response'],
                    'status': 'success',
                    'agent_handled': True,
                    'requires_confirmation': agent_result.get('requires_confirmation', False),
                    'confirmation_data': agent_result.get('confirmation_data', {}),
                    'data': agent_result.get('data', {})
                })

        # Check if LLM is enabled and configured
        if not config.get('enabled', False):
            return enhanced_fallback_response(user_query, current_session_id, user_id)

        # Get enhanced pharmacy context
        pharmacy_context = get_pharmacy_context()

        # Create enhanced system prompt with comprehensive data
        system_prompt = f"""You are an advanced AI assistant for ALORF HOSPITAL Pharmacy Management System with comprehensive database access and administrative capabilities.

CURRENT PHARMACY STATUS:
- Total Medicines: {pharmacy_context.get('total_counts', {}).get('medicines', 0)}
- Total Patients: {pharmacy_context.get('total_counts', {}).get('patients', 0)}
- Total Suppliers: {pharmacy_context.get('total_counts', {}).get('suppliers', 0)}
- Total Departments: {pharmacy_context.get('total_counts', {}).get('departments', 0)}
- Total Stores: {pharmacy_context.get('total_counts', {}).get('stores', 0)}

INVENTORY OVERVIEW:
- Medicines in Stock: {pharmacy_context.get('total_medicines_in_stock', 0)}
- Out of Stock: {pharmacy_context.get('out_of_stock_count', 0)}
- Low Stock Alerts: {len(pharmacy_context.get('low_stock_medicines', []))}

TOP STOCK MEDICINES:
{chr(10).join([f"- {med.get('name', 'Unknown')}: {med.get('stock', 0)} units" for med in pharmacy_context.get('highest_stock_medicines', [])[:3]])}

LOW STOCK ALERTS:
{chr(10).join([f"- {item.get('name', 'Unknown')}: {item.get('current_stock', 0)} units (limit: {item.get('low_stock_limit', 0)})" for item in pharmacy_context.get('low_stock_medicines', [])[:3]])}

RECENT ACTIVITY:
- Consumption Records (30 days): {pharmacy_context.get('recent_consumption_count', 0)}
- Recent Purchase Cost: ${pharmacy_context.get('recent_purchase_cost', 0):,.2f}

MEDICINE CATEGORIES:
{chr(10).join([f"- {cat}: {count} medicines" for cat, count in list(pharmacy_context.get('medicine_categories', {}).items())[:5]])}

You can provide detailed analytics, answer complex queries about inventory, consumption patterns, patient data, and suggest actionable insights. Be specific with data and provide comprehensive responses."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]

        # Call LLM API
        response = call_llm_api(messages, config)

        # Save AI response to chat history
        chat_history_manager.add_message(
            current_session_id, user_id, response, 'ai',
            {'llm_handled': True, 'provider': config.get('provider', 'openai')}
        )

        return jsonify({
            'response': response,
            'status': 'success',
            'llm_handled': True,
            'context_data': pharmacy_context
        })

    except Exception as e:
        print(f"Enhanced query error: {e}")
        # Fallback to enhanced responses
        return enhanced_fallback_response(user_query, current_session_id, user_id)

@chatbot_bp.route('/confirm', methods=['POST'])
@admin_required
def confirm_action():
    """Handle confirmation for administrative actions"""
    try:
        user_input = request.json.get('confirmation', '')
        user_id = session.get('user_id', 'admin')

        # Check for deletion confirmation
        delete_match = re.search(r'CONFIRM DELETE MEDICINE (\w+)', user_input, re.IGNORECASE)
        if delete_match:
            medicine_id = delete_match.group(1)

            # Verify medicine exists
            medicines = get_medicines()
            medicine = next((m for m in medicines if m['id'] == medicine_id), None)

            if not medicine:
                return jsonify({
                    'response': f"Medicine with ID '{medicine_id}' not found.",
                    'status': 'error'
                })

            # Perform deletion
            delete_medicine(medicine_id)

            # Log the action
            log_activity('DELETE', 'medicine', user_id, {
                'medicine_id': medicine_id,
                'medicine_name': medicine.get('name', 'Unknown'),
                'via': 'AI_assistant_confirmed'
            })

            response = f"✅ **Medicine Deleted Successfully!**\n\n"
            response += f"• **Medicine:** {medicine.get('name', 'Unknown')}\n"
            response += f"• **ID:** {medicine_id}\n\n"
            response += "The medicine and all its inventory records have been removed from the system."

            return jsonify({
                'response': response,
                'status': 'success',
                'action_completed': 'delete_medicine'
            })

        # Check for transfer confirmation
        transfer_match = re.search(r'CONFIRM TRANSFER (\w+) (\d+) (\w+) (\w+)', user_input, re.IGNORECASE)
        if transfer_match:
            medicine_id, quantity, source_dept_id, dest_dept_id = transfer_match.groups()
            quantity = int(quantity)

            try:
                # Perform the transfer
                # Subtract from source
                update_store_inventory(source_dept_id, [{'medicine_id': medicine_id, 'quantity': quantity}], 'subtract')
                # Add to destination
                update_store_inventory(dest_dept_id, [{'medicine_id': medicine_id, 'quantity': quantity}], 'add')

                # Log the action
                log_activity('TRANSFER', 'inventory', user_id, {
                    'medicine_id': medicine_id,
                    'quantity': quantity,
                    'source_dept_id': source_dept_id,
                    'dest_dept_id': dest_dept_id,
                    'via': 'AI_assistant_confirmed'
                })

                response = f"✅ **Transfer Completed Successfully!**\n\n"
                response += f"• **Medicine ID:** {medicine_id}\n"
                response += f"• **Quantity:** {quantity} units\n"
                response += f"• **From:** Department {source_dept_id}\n"
                response += f"• **To:** Department {dest_dept_id}\n\n"
                response += "The inventory has been updated in both departments."

                return jsonify({
                    'response': response,
                    'status': 'success',
                    'action_completed': 'transfer_inventory'
                })
            except Exception as e:
                return jsonify({
                    'response': f"Transfer failed: {str(e)}",
                    'status': 'error'
                })

        # If no confirmation pattern matched
        return jsonify({
            'response': "Confirmation not recognized. Please use the exact confirmation format provided.",
            'status': 'error'
        })

    except Exception as e:
        return jsonify({
            'response': f"Error processing confirmation: {str(e)}",
            'status': 'error'
        })

def enhanced_fallback_response(user_query, session_id, user_id):
    """Enhanced fallback response system with comprehensive data access"""
    try:
        # Use the AI agent for fallback as well
        agent_result = pharmacy_agent.process_command(user_query)

        if agent_result.get('success'):
            # Save AI response to chat history
            chat_history_manager.add_message(
                session_id, user_id, agent_result['response'], 'ai',
                {'fallback_handled': True, 'data': agent_result.get('data', {})}
            )

            return jsonify({
                'response': agent_result['response'],
                'status': 'success',
                'fallback_handled': True
            })

        # If agent couldn't handle it, provide enhanced fallback
        user_query_lower = user_query.lower()

        # Get comprehensive data for better responses
        comprehensive_data = chatbot_db.get_comprehensive_data()

        if 'highest stock' in user_query_lower:
            inventory_summary = comprehensive_data.get('inventory_summary', {})
            highest_stock = inventory_summary.get('highest_stock_medicines', [])

            if highest_stock:
                top_medicine = highest_stock[0]
                response = f"**Highest Stock Medicine:**\n"
                response += f"• {top_medicine.get('name', 'Unknown')}: {top_medicine.get('stock', 0)} units\n"
                response += f"• Category: {top_medicine.get('category', 'Unknown')}"
            else:
                response = "No stock data available."

        elif any(word in user_query_lower for word in ['low stock', 'running low']):
            low_stock = comprehensive_data.get('low_stock_alerts', [])

            if low_stock:
                response = f"**Low Stock Medicines ({len(low_stock)} total):**\n\n"
                for item in low_stock[:5]:
                    response += f"• {item.get('name', 'Unknown')}: {item.get('current_stock', 0)} units (limit: {item.get('low_stock_limit', 0)})\n"
                if len(low_stock) > 5:
                    response += f"\n...and {len(low_stock) - 5} more medicines."
            else:
                response = "Great news! All medicines are currently well-stocked above their low stock limits."

        elif 'analytics' in user_query_lower or 'summary' in user_query_lower:
            analytics = comprehensive_data.get('analytics', {})
            total_counts = analytics.get('total_counts', {})

            response = f"**Pharmacy Analytics Summary:**\n\n"
            response += f"📊 **Total Counts:**\n"
            for entity, count in total_counts.items():
                response += f"• {entity.title()}: {count}\n"

            response += f"\n💰 **Financial:**\n"
            response += f"• Recent Purchase Cost (30 days): ${analytics.get('recent_purchase_cost', 0):,.2f}\n"

            response += f"\n📈 **Activity:**\n"
            response += f"• Recent Consumption Records: {analytics.get('recent_consumption_count', 0)}\n"

        else:
            # Default enhanced response
            response = """🤖 **Enhanced AI Pharmacy Assistant**

I can help you with comprehensive pharmacy management:

**📊 Advanced Analytics:**
• "What is the highest stock medicine and its current level?"
• "Which patient has consumed the most medicines this month?"
• "Show me the top 5 most expensive purchases this year"
• "Which department has the lowest average stock levels?"
• "Show me medicines expiring within 30 days"

**🔧 Administrative Operations:**
• "Add a new medicine called [name] with category [category]"
• "Update patient [ID] medical history to [new history]"
• "Delete medicine with ID [ID]" (with confirmation)
• "Transfer [quantity] units of [medicine] from [source] to [destination]"

**🔍 Real-time Data Access:**
• Complete access to all pharmacy data
• Cross-module operations and analytics
• Intelligent search and filtering

Try asking me anything about your pharmacy operations!"""

        # Save AI response to chat history
        chat_history_manager.add_message(
            session_id, user_id, response, 'ai',
            {'enhanced_fallback': True}
        )

        return jsonify({'response': response, 'status': 'success', 'enhanced_fallback': True})

    except Exception as e:
        error_response = f'Sorry, I encountered an error: {str(e)}'
        # Save error response to chat history
        chat_history_manager.add_message(
            session_id, user_id, error_response, 'ai',
            {'error': True, 'enhanced_fallback': True}
        )
        return jsonify({'response': error_response, 'status': 'error'}), 500
