"""
Chatbot Blueprint Package

AI Chatbot functionality for admin users.
Split into routes.py for chat interface and config_routes.py for configuration management.
"""

from flask import Blueprint
from .routes import chatbot_bp
from .config_routes import chatbot_config_bp

__all__ = ['chatbot_bp', 'chatbot_config_bp']
