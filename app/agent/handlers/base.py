"""
Base Handler Class
Abstract base class for all query handlers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseHandler(ABC):
    """Abstract base class for query handlers"""

    def __init__(self):
        """Initialize the handler"""
        pass

    @abstractmethod
    def can_handle(self, query_type: str) -> bool:
        """Check if this handler can process the given query type

        Args:
            query_type: The type of query

        Returns:
            bool: True if this handler can process the query
        """
        pass

    @abstractmethod
    def handle(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the query and return a response

        Args:
            query_data: Query data including type, input, user_id

        Returns:
            dict: Response with success, response, and optional data
        """
        pass

    def get_supported_query_types(self) -> list[str]:
        """Get list of query types supported by this handler

        Returns:
            list: List of query types
        """
        return []

    def format_response(self, title: str, items: list, item_format: str = None) -> str:
        """Format a response with title and items

        Args:
            title: Response title
            items: List of items to include
            item_format: Optional format string for each item

        Returns:
            str: Formatted response
        """
        response = f"{title}\n\n"

        if not items:
            response += "No data available."
            return response

        for i, item in enumerate(items, 1):
            if item_format:
                response += f"{i}. {item_format.format(**item)}\n"
            else:
                response += f"{i}. {item}\n"

        return response

    def format_error_response(self, error_message: str) -> Dict[str, Any]:
        """Format an error response

        Args:
            error_message: Error message

        Returns:
            dict: Error response
        """
        return {
            'success': False,
            'response': error_message,
            'error': error_message
        }

    def format_success_response(self, response: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format a success response

        Args:
            response: Response message
            data: Optional data dictionary

        Returns:
            dict: Success response
        """
        result = {
            'success': True,
            'response': response
        }

        if data:
            result['data'] = data

        return result
