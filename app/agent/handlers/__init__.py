"""
Handler Registry
Centralized registry for all query handlers
"""

from .base import BaseHandler
from .medicine import MedicineHandler
from .crud import CRUDHandler


class HandlerRegistry:
    """Registry for managing query handlers"""

    def __init__(self):
        """Initialize the registry with all handlers"""
        self._handlers = []
        self._handler_map = {}

        # Register all handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register the default set of handlers"""
        self.register(MedicineHandler())
        self.register(CRUDHandler())

    def register(self, handler: BaseHandler) -> None:
        """Register a handler

        Args:
            handler: Handler instance to register
        """
        self._handlers.append(handler)

        # Map query types to handlers
        for query_type in handler.get_supported_query_types():
            if query_type not in self._handler_map:
                self._handler_map[query_type] = []
            self._handler_map[query_type].append(handler)

    def get_handler(self, query_type: str) -> BaseHandler:
        """Get a handler for the given query type

        Args:
            query_type: The type of query

        Returns:
            BaseHandler: Handler that can process the query, or None
        """
        handlers = self._handler_map.get(query_type, [])
        return handlers[0] if handlers else None

    def handle(self, query_data: dict) -> dict:
        """Handle a query using the appropriate handler

        Args:
            query_data: Query data dictionary

        Returns:
            dict: Handler response
        """
        query_type = query_data.get('type')

        handler = self.get_handler(query_type)
        if handler:
            return handler.handle(query_data)

        return {
            'success': False,
            'response': f"No handler found for query type: {query_type}"
        }

    def get_all_supported_queries(self) -> list[str]:
        """Get all supported query types

        Returns:
            list: List of all supported query types
        """
        return list(self._handler_map.keys())

    def can_handle(self, query_type: str) -> bool:
        """Check if any handler can process the query type

        Args:
            query_type: The type of query

        Returns:
            bool: True if a handler is available
        """
        return query_type in self._handler_map


# Global registry instance
handler_registry = HandlerRegistry()
