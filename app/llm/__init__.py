"""
LLM Provider Package
Abstract LLM provider interface with pluggable implementations
"""

from .base import (
    BaseLLMProvider,
    LLMProviderError,
    LLMConfigError,
    LLMAPIError
)
from .providers import (
    OpenAIProvider,
    OpenRouterProvider,
    GoogleProvider,
    PROVIDER_CLASSES,
    DEFAULT_MODELS
)
from .factory import (
    create_llm_provider,
    get_available_providers,
    get_default_model
)

__all__ = [
    # Base classes
    'BaseLLMProvider',
    'LLMProviderError',
    'LLMConfigError',
    'LLMAPIError',

    # Providers
    'OpenAIProvider',
    'OpenRouterProvider',
    'GoogleProvider',

    # Factory functions
    'create_llm_provider',
    'get_available_providers',
    'get_default_model',

    # Constants
    'PROVIDER_CLASSES',
    'DEFAULT_MODELS'
]
