"""
Users Blueprint Package

User management functionality extracted from settings blueprint.
Handles all user CRUD operations, password resets, and department user creation.
"""

from flask import Blueprint
from .routes import users_bp

__all__ = ['users_bp']
