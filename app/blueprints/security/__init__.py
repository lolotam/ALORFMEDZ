"""
Security Blueprint Package

Security settings and audit functionality extracted from settings blueprint.
Handles security dashboard, audit logs, log export, and data erasure.
"""

from flask import Blueprint
from .routes import security_bp

__all__ = ['security_bp']
