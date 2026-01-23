"""
LLM Provider Factory
Factory for creating LLM provider instances
"""

from typing import Dict, Any, Optional
from .base import BaseLLMProvider, LLMConfigError
from .providers import (
    PROVIDER_CLASSES,
    DEFAULT_MODELS,
    OpenAIProvider,
    OpenRouterProvider,
    GoogleProvider
)


def create_llm_provider(config: Dict[str, Any]) -> BaseLLMProvider:
    """Create an LLM provider instance based on configuration

    Args:
        config: Configuration dictionary with 'provider' key and provider-specific keys

    Returns:
        BaseLLMProvider: Provider instance

    Raises:
        LLMConfigError: If provider is unknown or configuration is invalid

    Example:
        >>> config = {'provider': 'openai', 'openai_api_key': 'sk-...'}
        >>> provider = create_llm_provider(config)
        >>> response = provider.call(messages)
    """
    provider_name = config.get('provider', 'openai').lower()

    # Set default model if not specified
    if 'model' not in config:
        config['model'] = DEFAULT_MODELS.get(provider_name, 'default')

    provider_class = PROVIDER_CLASSES.get(provider_name)
    if not provider_class:
        raise LLMConfigError(f"Unknown provider: {provider_name}. Available: {list(PROVIDER_CLASSES.keys())}")

    try:
        return provider_class(config)
    except Exception as e:
        raise LLMConfigError(f"Failed to create {provider_name} provider: {str(e)}")


def get_available_providers() -> list[str]:
    """Get list of available provider names

    Returns:
        list[str]: List of provider names
    """
    return list(PROVIDER_CLASSES.keys())


def get_default_model(provider: str) -> Optional[str]:
    """Get default model for a provider

    Args:
        provider: Provider name

    Returns:
        str: Default model name or None
    """
    return DEFAULT_MODELS.get(provider.lower())
