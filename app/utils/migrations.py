"""
Database Migration Utilities
Handles database schema updates and data migrations
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from app.utils.database import load_data, save_data, get_medicines

def migrate_medicine_fields():
    """
    Migration: Add new fields to existing medicine records
    Adds expiry_date, batch_number, and barcode_number fields to existing medicines
    """
    print("Starting medicine fields migration...")
    
    try:
        # Load existing medicines
        medicines = get_medicines()
        
        if not medicines:
            print("No medicines found. Migration not needed.")
            return True, "No medicines to migrate"
        
        updated_count = 0
        
        # Update each medicine record
        for medicine in medicines:
            updated = False
            
            # Add expiry_date field if missing
            if 'expiry_date' not in medicine:
                medicine['expiry_date'] = None
                updated = True
            
            # Add batch_number field if missing
            if 'batch_number' not in medicine:
                medicine['batch_number'] = None
                updated = True
            
            # Add barcode_number field if missing
            if 'barcode_number' not in medicine:
                medicine['barcode_number'] = None
                updated = True
            
            # Add migration timestamp if updated
            if updated:
                medicine['migrated_at'] = datetime.now().isoformat()
                updated_count += 1
        
        # Save updated medicines
        if updated_count > 0:
            save_data('medicines', medicines)
            print(f"Migration completed successfully. Updated {updated_count} medicine records.")
            return True, f"Successfully migrated {updated_count} medicine records"
        else:
            print("All medicine records already have the new fields. No migration needed.")
            return True, "All records already up to date"
            
    except Exception as e:
        error_msg = f"Migration failed: {str(e)}"
        print(error_msg)
        return False, error_msg

def check_migration_status():
    """
    Check if medicine fields migration is needed
    Returns True if migration is needed, False otherwise
    """
    try:
        medicines = get_medicines()
        
        if not medicines:
            return False  # No medicines, no migration needed
        
        # Check if any medicine is missing the new fields
        for medicine in medicines:
            if ('expiry_date' not in medicine or 
                'batch_number' not in medicine or 
                'barcode_number' not in medicine):
                return True  # Migration needed
        
        return False  # All medicines have the new fields
        
    except Exception as e:
        print(f"Error checking migration status: {str(e)}")
        return False

def run_all_migrations():
    """
    Run all available migrations
    """
    migrations = [
        {
            'name': 'Medicine Fields Migration',
            'function': migrate_medicine_fields,
            'check_function': check_migration_status
        }
    ]
    
    results = []
    
    for migration in migrations:
        print(f"\n--- {migration['name']} ---")
        
        # Check if migration is needed
        if migration['check_function']():
            print(f"Running {migration['name']}...")
            success, message = migration['function']()
            results.append({
                'name': migration['name'],
                'success': success,
                'message': message
            })
        else:
            print(f"{migration['name']} not needed - skipping")
            results.append({
                'name': migration['name'],
                'success': True,
                'message': 'Migration not needed'
            })
    
    return results

def create_migration_log(results: List[Dict]):
    """
    Create a log file of migration results
    """
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'migrations': results
    }
    
    # Ensure logs directory exists
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Write log file
    log_file = os.path.join(logs_dir, f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"Migration log saved to: {log_file}")
    return log_file

if __name__ == "__main__":
    """
    Run migrations when script is executed directly
    """
    print("=== Database Migration Tool ===")
    print("Running all available migrations...\n")
    
    results = run_all_migrations()
    
    print("\n=== Migration Summary ===")
    for result in results:
        status = "✓ SUCCESS" if result['success'] else "✗ FAILED"
        print(f"{status}: {result['name']} - {result['message']}")
    
    # Create migration log
    log_file = create_migration_log(results)
    
    print(f"\nMigration process completed. Log saved to: {log_file}")
