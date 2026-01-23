"""
Database layer - Repository pattern with backward compatibility

This package provides organized database access through entity-specific modules.
All functions are re-exported for backward compatibility.

DEPRECATED: Direct imports will be replaced with service layer in Phase 3.
"""

# Import constants explicitly (wildcard doesn't import them)
from .base import DB_FILES, DATA_DIR

# Re-export all functions for backward compatibility
from .base import *
from .users import *
from .medicines import *
from .patients import *
from .suppliers import *
from .departments import *
from .stores import *
from .purchases import *
from .consumption import *
from .transfers import *
from .activity import *

__all__ = [
    # Base utilities
    'load_data', 'save_data', 'generate_id', 'renumber_ids',
    'ensure_main_entities', 'init_database',
    'cascade_update_medicine_references', 'cascade_update_patient_references',
    'cascade_update_supplier_references', 'cascade_update_department_references',
    'cascade_update_store_references', 'cascade_update_user_references',
    'log_history',
    # Base constants
    'DB_FILES', 'DATA_DIR',

    # User management
    'get_users', 'validate_user', 'save_user', 'update_user', 'delete_user',
    'get_user_by_id', 'get_user_by_username', 'get_users_by_department',
    'handle_failed_login', 'unlock_user_account', 'validate_password_strength',
    'generate_username', 'generate_secure_password', 'create_department_user',
    'delete_department_users',

    # Medicine management
    'get_medicines', 'save_medicine', 'update_medicine', 'delete_medicine',
    'migrate_medicine_fields',

    # Patient management
    'get_patients', 'save_patient', 'update_patient', 'delete_patient',

    # Supplier management
    'get_suppliers', 'save_supplier', 'update_supplier', 'delete_supplier',

    # Department management
    'get_departments', 'save_department', 'save_department_with_user',
    'update_department', 'delete_department',

    # Store management
    'get_stores', 'get_store_by_id', 'update_store',
    'create_store_for_department', 'delete_store', 'delete_department_and_store',
    'update_main_store_inventory',

    # Purchase management
    'get_purchases', 'save_purchase', 'update_purchase', 'delete_purchase',

    # Consumption management
    'get_consumption', 'save_consumption', 'update_consumption', 'delete_consumption',
    'get_medicine_stock', 'update_store_inventory', 'get_low_stock_medicines',
    'get_available_medicines_for_consumption', 'validate_consumption_stock',
    'get_stock_status',

    # Transfer management
    'get_transfers', 'save_transfer', 'process_inventory_transfer',
    'get_medicine_name', 'delete_transfer', 'update_transfer',

    # Activity logging
    'log_activity', 'get_history', 'get_user_activity_summary',

    # Forms
    'get_forms',
]
