"""
Base Repository Abstract Class
Defines the interface for repository pattern implementation
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class BaseRepository(ABC):
    """
    Abstract base class for repository pattern.

    This class defines the standard CRUD interface that all repositories
    should implement. The actual implementations are in the entity-specific
    modules (users.py, medicines.py, etc.).

    Usage:
        While the current implementation uses function-based repositories,
        this abstract class documents the expected interface for future
        refactoring to class-based repositories.

    Example future implementation:
        class UserRepository(BaseRepository):
            def get_all(self) -> List[Dict[str, Any]]:
                return get_users()

            def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
                return get_user_by_id(id)

            # ... etc
    """

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        """
        Get all records from the repository.

        Returns:
            List of all records as dictionaries.
        """
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single record by ID.

        Args:
            id: The record ID to look up.

        Returns:
            The record as a dictionary, or None if not found.
        """
        pass

    @abstractmethod
    def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save a new record to the repository.

        Args:
            data: The record data to save.

        Returns:
            The saved record including generated ID and timestamps.
        """
        pass

    @abstractmethod
    def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing record.

        Args:
            id: The record ID to update.
            data: The fields to update.

        Returns:
            The updated record, or None if not found.
        """
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """
        Delete a record by ID.

        Args:
            id: The record ID to delete.

        Returns:
            True if deleted, False otherwise.
        """
        pass


class QueryBuilder:
    """
    Helper class for building database queries.

    This provides a fluent interface for filtering and querying data.
    """

    def __init__(self, data: List[Dict[str, Any]]):
        self._data = data
        self._filters = []

    def where(self, field: str, value: Any) -> 'QueryBuilder':
        """Filter records where field equals value"""
        self._filters.append(lambda x: x.get(field) == value)
        return self

    def where_in(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """Filter records where field is in values"""
        self._filters.append(lambda x: x.get(field) in values)
        return self

    def where_contains(self, field: str, value: str) -> 'QueryBuilder':
        """Filter records where field contains value (case-insensitive)"""
        self._filters.append(
            lambda x: value.lower() in str(x.get(field, '')).lower()
        )
        return self

    def order_by(self, field: str, descending: bool = False) -> 'QueryBuilder':
        """Order results by field"""
        self._data = sorted(
            self._data,
            key=lambda x: x.get(field, ''),
            reverse=descending
        )
        return self

    def limit(self, count: int) -> 'QueryBuilder':
        """Limit results to count"""
        self._data = self._data[:count]
        return self

    def execute(self) -> List[Dict[str, Any]]:
        """Execute the query and return results"""
        result = self._data
        for filter_fn in self._filters:
            result = [x for x in result if filter_fn(x)]
        return result


__all__ = ['BaseRepository', 'QueryBuilder']
