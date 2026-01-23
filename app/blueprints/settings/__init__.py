"""
Settings Blueprint Package (Refactored)

Settings dashboard now contains only the main settings dashboard and about page.
User management, backup, and security functionality have been moved to their own blueprints.
"""

from flask import Blueprint
from .routes import settings_bp

__all__ = ['settings_bp']
