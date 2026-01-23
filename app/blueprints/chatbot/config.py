"""
Chatbot Configuration

Configuration loading and saving utilities.
"""

import json
import os

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
