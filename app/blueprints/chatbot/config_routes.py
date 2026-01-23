"""
Chatbot Configuration Routes

Configuration management routes for the AI chatbot.
Separated from main chat routes for better organization.
"""

import json
import os
import requests
import time
from flask import Blueprint, jsonify, request
from app.utils.decorators import admin_required

# Create a separate blueprint for config routes
chatbot_config_bp = Blueprint('chatbot_config', __name__)

# Configuration file path
CONFIG_FILE = 'data/chatbot_config.json'

# Cache for OpenRouter models (5 minute TTL)
_openrouter_models_cache = {
    'models': [],
    'timestamp': None
}


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


@chatbot_config_bp.route('/config', methods=['GET', 'POST'])
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


@chatbot_config_bp.route('/test-connection', methods=['POST'])
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


@chatbot_config_bp.route('/fetch-openrouter-models', methods=['GET'])
@admin_required
def fetch_openrouter_models():
    """Fetch all available models from OpenRouter API"""
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


@chatbot_config_bp.route('/models', methods=['GET'])
@admin_required
def get_models():
    """Get available models for current provider"""
    config = load_chatbot_config()
    provider = config.get('provider', 'openai')
    available_models = config.get('available_models', {})

    return jsonify({
        'provider': provider,
        'models': available_models.get(provider, [])
    })
