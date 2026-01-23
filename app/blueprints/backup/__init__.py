"""
Backup Blueprint Package

Backup and restore functionality extracted from settings blueprint.
Handles full system backups, individual file backups, backup management,
and data restoration.
"""

from flask import Blueprint
from .routes import backup_bp

__all__ = ['backup_bp']
