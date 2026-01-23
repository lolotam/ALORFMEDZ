"""
LLM Provider Base Interface
Abstract base class for all LLM provider implementations
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the provider with configuration

        Args:
            config: Provider configuration dictionary
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider configuration

        Raises:
            ValueError: If configuration is invalid
        """
        pass

    @abstractmethod
    def call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call the LLM API with messages

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Returns:
            str: The LLM response text

        Raises:
            Exception: If API call fails
        """
        pass

    @abstractmethod
    def get_context(self) -> Dict[str, Any]:
        """Get provider-specific context for prompts

        Returns:
            dict: Context data for prompt building
        """
        pass

    def get_model(self) -> str:
        """Get the configured model name

        Returns:
            str: Model name
        """
        return self.config.get('model', 'default')

    def get_max_tokens(self) -> int:
        """Get configured max tokens

        Returns:
            int: Max tokens
        """
        return self.config.get('max_tokens', 1000)

    def get_temperature(self) -> float:
        """Get configured temperature

        Returns:
            float: Temperature value
        """
        return self.config.get('temperature', 0.7)


class LLMProviderError(Exception):
    """Base exception for LLM provider errors"""
    pass


class LLMConfigError(LLMProviderError):
    """Exception raised for configuration errors"""
    pass


class LLMAPIError(LLMProviderError):
    """Exception raised for API call errors"""
    pass
