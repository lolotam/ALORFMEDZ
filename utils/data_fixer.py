"""
Data Fixer Utility
Fixes data consistency issues found by validation
"""

import json
import random
from datetime import datetime
from typing import Dict, List
from utils.database import (
    get_transfers, get_patients, get_stores, save_data
)

class DataFixer:
    def __init__(self):
        self.transfers = get_transfers()
        self.patients = get_patients()
        self.stores = get_stores()
        self.valid_store_ids = [s['id'] for s in self.stores]

    def fix_transfer_store_references(self):
        """Fix invalid store references in transfer records"""
        print("Fixing transfer store references...")
        fixed_count = 0
        
        for transfer in self.transfers:
            updated = False
            
            # Fix invalid source store ID
            if transfer.get('source_store_id') not in self.valid_store_ids:
                old_id = transfer.get('source_store_id')
                transfer['source_store_id'] = random.choice(self.valid_store_ids)
                print(f"  Fixed transfer {transfer['id']}: source store {old_id} -> {transfer['source_store_id']}")
                updated = True
            
            # Fix invalid destination store ID
            if transfer.get('destination_store_id') not in self.valid_store_ids:
                old_id = transfer.get('destination_store_id')
                # Ensure destination is different from source
                available_stores = [sid for sid in self.valid_store_ids if sid != transfer.get('source_store_id')]
                transfer['destination_store_id'] = random.choice(available_stores)
                print(f"  Fixed transfer {transfer['id']}: destination store {old_id} -> {transfer['destination_store_id']}")
                updated = True
            
            # Ensure source and destination are different
            if transfer.get('source_store_id') == transfer.get('destination_store_id'):
                available_stores = [sid for sid in self.valid_store_ids if sid != transfer.get('source_store_id')]
                transfer['destination_store_id'] = random.choice(available_stores)
                print(f"  Fixed transfer {transfer['id']}: made destination different from source")
                updated = True
            
            if updated:
                transfer['updated_at'] = datetime.now().isoformat()
                fixed_count += 1
        
        if fixed_count > 0:
            save_data('transfers', self.transfers)
            print(f"Fixed {fixed_count} transfer records")
        
        return fixed_count

    def fix_patient_missing_age(self):
        """Fix patients with missing age information"""
        print("Fixing patients with missing age...")
        fixed_count = 0
        
        for patient in self.patients:
            if not patient.get('age') or patient.get('age') == 0:
                # Assign random realistic age (18-85)
                patient['age'] = random.randint(18, 85)
                patient['updated_at'] = datetime.now().isoformat()
                print(f"  Fixed patient {patient['id']}: added age {patient['age']}")
                fixed_count += 1
        
        if fixed_count > 0:
            save_data('patients', self.patients)
            print(f"Fixed {fixed_count} patient records")
        
        return fixed_count

    def fix_all_issues(self):
        """Fix all identified data issues"""
        print("=== Starting Data Fixes ===\n")
        
        results = {
            'transfers': self.fix_transfer_store_references(),
            'patients': self.fix_patient_missing_age()
        }
        
        print(f"\n=== Data Fix Summary ===")
        total_fixed = sum(results.values())
        for data_type, count in results.items():
            print(f"{data_type.capitalize()}: {count} records fixed")
        print(f"Total records fixed: {total_fixed}")
        
        return results

if __name__ == "__main__":
    fixer = DataFixer()
    fixer.fix_all_issues()
