"""
Intent Pattern Definitions
Defines query intent patterns for intelligent matching
"""

from typing import Dict, List, Optional


class IntentPatterns:
    """Intent patterns for query classification"""

    # Query intent patterns
    INTENT_PATTERNS = {
        'count_query': [
            'how many',
            'count',
            'total number',
            'number of'
        ],
        'list_query': [
            'list',
            'show me',
            'give me',
            'display',
            'what are',
            'what is',
            'show all'
        ],
        'analysis_query': [
            'analyze',
            'analysis',
            'breakdown',
            'summary',
            'overview',
            'statistics',
            'report'
        ],
        'comparison_query': [
            'compare',
            'versus',
            'vs',
            'difference between'
        ],
        'search_query': [
            'find',
            'search',
            'look for',
            'locate'
        ],
        'status_query': [
            'status',
            'condition',
            'state',
            'situation'
        ]
    }

    # CRUD operation patterns
    CRUD_PATTERNS = {
        'create': [
            'add',
            'create',
            'new',
            'register',
            'insert',
            'make'
        ],
        'read': [
            'show',
            'get',
            'list',
            'display',
            'view',
            'find'
        ],
        'update': [
            'update',
            'change',
            'modify',
            'edit',
            'set'
        ],
        'delete': [
            'delete',
            'remove',
            'erase',
            'eliminate',
            'destroy'
        ]
    }

    # Operation patterns
    OPERATION_PATTERNS = {
        'transfer': [
            'transfer',
            'move',
            'shift',
            'relocate',
            'send to'
        ],
        'consume': [
            'consume',
            'use',
            'dispense',
            'take',
            'administer'
        ],
        'purchase': [
            'purchase',
            'buy',
            'order',
            'procure',
            'acquire'
        ],
        'restock': [
            'restock',
            'refill',
            'replenish',
            'add stock'
        ]
    }

    @classmethod
    def identify_intent(cls, text: str) -> Optional[str]:
        """Identify the intent of the query

        Args:
            text: Query text

        Returns:
            str or None: Identified intent type
        """
        text_lower = text.lower()

        for intent, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return intent

        return None

    @classmethod
    def identify_crud_operation(cls, text: str) -> Optional[str]:
        """Identify CRUD operation type

        Args:
            text: Query text

        Returns:
            str or None: CRUD operation type
        """
        text_lower = text.lower()

        for operation, patterns in cls.CRUD_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return operation

        return None

    @classmethod
    def identify_operation(cls, text: str) -> Optional[str]:
        """Identify specific operation type

        Args:
            text: Query text

        Returns:
            str or None: Operation type
        """
        text_lower = text.lower()

        for operation, patterns in cls.OPERATION_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return operation

        return None

    @classmethod
    def get_all_intents(cls) -> List[str]:
        """Get all available intent types

        Returns:
            list[str]: List of intent types
        """
        return list(cls.INTENT_PATTERNS.keys())

    @classmethod
    def get_all_crud_operations(cls) -> List[str]:
        """Get all CRUD operation types

        Returns:
            list[str]: List of CRUD operations
        """
        return list(cls.CRUD_PATTERNS.keys())

    @classmethod
    def get_all_operations(cls) -> List[str]:
        """Get all operation types

        Returns:
            list[str]: List of operations
        """
        return list(cls.OPERATION_PATTERNS.keys())


# Global instance
intent_patterns = IntentPatterns()
