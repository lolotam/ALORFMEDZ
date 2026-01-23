"""
LLM Provider Implementations
Concrete implementations for OpenAI, OpenRouter, and Google Gemini
"""

import requests
from typing import Dict, List, Any
from .base import BaseLLMProvider, LLMConfigError, LLMAPIError


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API LLM provider"""

    def _validate_config(self) -> None:
        """Validate OpenAI configuration"""
        api_key = self.config.get('openai_api_key')
        if not api_key:
            raise LLMConfigError("OpenAI API key not configured")

    def call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call OpenAI API"""
        api_key = self.config.get('openai_api_key')

        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': kwargs.get('model', self.get_model()),
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', self.get_max_tokens()),
                'temperature': kwargs.get('temperature', self.get_temperature())
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise LLMAPIError(f"OpenAI API error: {response.status_code} - {response.text}")

    def get_context(self) -> Dict[str, Any]:
        """Get OpenAI-specific context"""
        return {
            'provider': 'openai',
            'model': self.get_model(),
            'api_base': 'https://api.openai.com/v1'
        }


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API LLM provider"""

    def _validate_config(self) -> None:
        """Validate OpenRouter configuration"""
        api_key = self.config.get('openrouter_api_key')
        if not api_key:
            raise LLMConfigError("OpenRouter API key not configured")

    def call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call OpenRouter API"""
        api_key = self.config.get('openrouter_api_key')

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': kwargs.get('model', self.get_model()),
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', self.get_max_tokens()),
                'temperature': kwargs.get('temperature', self.get_temperature())
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise LLMAPIError(f"OpenRouter API error: {response.status_code} - {response.text}")

    def get_context(self) -> Dict[str, Any]:
        """Get OpenRouter-specific context"""
        return {
            'provider': 'openrouter',
            'model': self.get_model(),
            'api_base': 'https://openrouter.ai/api/v1'
        }


class GoogleProvider(BaseLLMProvider):
    """Google Gemini API LLM provider"""

    def _validate_config(self) -> None:
        """Validate Google configuration"""
        api_key = self.config.get('google_api_key')
        if not api_key:
            raise LLMConfigError("Google API key not configured")

    def call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call Google Gemini API"""
        api_key = self.config.get('google_api_key')

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

        model_name = kwargs.get('model', self.get_model())
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}',
            headers={
                'Content-Type': 'application/json'
            },
            json={
                'contents': gemini_contents,
                'generationConfig': {
                    'maxOutputTokens': kwargs.get('max_tokens', self.get_max_tokens()),
                    'temperature': kwargs.get('temperature', self.get_temperature())
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                raise LLMAPIError("No response from Google Gemini API")
        else:
            raise LLMAPIError(f"Google API error: {response.status_code} - {response.text}")

    def get_context(self) -> Dict[str, Any]:
        """Get Google-specific context"""
        return {
            'provider': 'google',
            'model': self.get_model(),
            'api_base': 'https://generativelanguage.googleapis.com'
        }


# Provider registry mapping
PROVIDER_CLASSES = {
    'openai': OpenAIProvider,
    'openrouter': OpenRouterProvider,
    'google': GoogleProvider
}

DEFAULT_MODELS = {
    'openai': 'gpt-4',
    'openrouter': 'meta-llama/llama-3.2-3b-instruct:free',
    'google': 'gemini-1.5-pro'
}
