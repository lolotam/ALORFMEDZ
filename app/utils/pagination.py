"""
Pagination Utilities

This module provides pagination utilities for large datasets.
"""

from flask import request, jsonify
from math import ceil
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PaginationHelper:
    """Helper class for pagination"""

    def __init__(self, page: int = 1, per_page: int = 25, max_per_page: int = 100):
        """
        Initialize pagination helper.

        Args:
            page: Current page number (1-indexed)
            per_page: Items per page
            max_per_page: Maximum items per page allowed
        """
        self.page = max(1, int(page))
        self.per_page = min(max(1, int(per_page)), max_per_page)
        self.max_per_page = max_per_page

    @staticmethod
    def from_request(default_per_page: int = 25, max_per_page: int = 100) -> 'PaginationHelper':
        """
        Create PaginationHelper from request args.

        Args:
            default_per_page: Default items per page
            max_per_page: Maximum items per page allowed

        Returns:
            PaginationHelper instance
        """
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', default_per_page, type=int)

        return PaginationHelper(page=page, per_page=per_page, max_per_page=max_per_page)

    def paginate(self, items: List[Any]) -> Dict[str, Any]:
        """
        Paginate a list of items.

        Args:
            items: List of items to paginate

        Returns:
            Dict containing pagination metadata and items
        """
        total = len(items)
        total_pages = ceil(total / self.per_page) if total > 0 else 0

        # Calculate start and end indices
        start_idx = (self.page - 1) * self.per_page
        end_idx = start_idx + self.per_page

        # Get items for current page
        page_items = items[start_idx:end_idx]

        return {
            'items': page_items,
            'total': total,
            'page': self.page,
            'per_page': self.per_page,
            'pages': total_pages,
            'has_prev': self.page > 1,
            'has_next': self.page < total_pages,
            'prev_num': self.page - 1 if self.page > 1 else None,
            'next_num': self.page + 1 if self.page < total_pages else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Return pagination parameters as dict"""
        return {
            'page': self.page,
            'per_page': self.per_page,
            'max_per_page': self.max_per_page
        }


def paginate_response(items: List[Any], page: int, per_page: int,
                     max_per_page: int = 100) -> Dict[str, Any]:
    """
    Create a paginated response.

    Args:
        items: List of items to paginate
        page: Current page number
        per_page: Items per page
        max_per_page: Maximum items per page

    Returns:
        Dict containing paginated data
    """
    helper = PaginationHelper(page=page, per_page=per_page, max_per_page=max_per_page)
    return helper.paginate(items)


def create_pagination_metadata(total: int, page: int, per_page: int,
                              max_per_page: int = 100) -> Dict[str, Any]:
    """
    Create pagination metadata without paginating items.

    Args:
        total: Total number of items
        page: Current page number
        per_page: Items per page
        max_per_page: Maximum items per page

    Returns:
        Dict containing pagination metadata
    """
    helper = PaginationHelper(page=page, per_page=per_page, max_per_page=max_per_page)
    total_pages = ceil(total / per_page) if total > 0 else 0

    return {
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < total_pages else None,
    }


def paginate_query(query, page: int, per_page: int, max_per_page: int = 100) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Paginate a database query.

    Args:
        query: SQLAlchemy query object or similar
        page: Current page number
        per_page: Items per page
        max_per_page: Maximum items per page

    Returns:
        Tuple of (paginated_items, metadata)
    """
    helper = PaginationHelper(page=page, per_page=per_page, max_per_page=max_per_page)

    # Get total count
    total = query.count()

    # Paginate
    items = query.offset((helper.page - 1) * helper.per_page).limit(helper.per_page).all()

    # Create metadata
    metadata = {
        'total': total,
        'page': helper.page,
        'per_page': helper.per_page,
        'pages': ceil(total / helper.per_page) if total > 0 else 0,
        'has_prev': helper.page > 1,
        'has_next': helper.page < ceil(total / helper.per_page) if total > 0 else False,
        'prev_num': helper.page - 1 if helper.page > 1 else None,
        'next_num': helper.page + 1 if helper.page < ceil(total / helper.per_page) else None,
    }

    return items, metadata


def lazy_load_paginated_response(items: List[Any], page: int, per_page: int,
                                 max_per_page: int = 100) -> Dict[str, Any]:
    """
    Create a response for lazy loading (load more) functionality.

    Args:
        items: List of items to paginate
        page: Current page number
        per_page: Items per page
        max_per_page: Maximum items per page

    Returns:
        Dict with items and pagination info for lazy loading
    """
    helper = PaginationHelper(page=page, per_page=per_page, max_per_page=max_per_page)
    result = helper.paginate(items)

    # Add lazy loading specific data
    result['lazy_load'] = {
        'current_page': page,
        'next_page': result['next_num'],
        'has_more': result['has_next'],
        'items_loaded': len(result['items'])
    }

    return result


def validate_pagination_params(page: Optional[int] = None,
                               per_page: Optional[int] = None,
                               max_per_page: int = 100) -> Tuple[int, int]:
    """
    Validate pagination parameters.

    Args:
        page: Page number
        per_page: Items per page
        max_per_page: Maximum items per page

    Returns:
        Tuple of (validated_page, validated_per_page)

    Raises:
        ValueError: If parameters are invalid
    """
    if page is None or page < 1:
        page = 1

    if per_page is None:
        per_page = 25
    elif per_page < 1:
        raise ValueError("per_page must be greater than 0")
    elif per_page > max_per_page:
        per_page = max_per_page

    return page, per_page
