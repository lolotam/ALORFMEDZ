"""
Data Validation Utility
Validates data consistency across all database tables
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
from utils.database import (
    get_medicines, get_patients, get_suppliers, get_consumption, 
    get_purchases, get_transfers, get_departments, get_stores
)

class DataValidator:
    def __init__(self):
        self.medicines = get_medicines()
        self.patients = get_patients()
        self.suppliers = get_suppliers()
        self.consumption = get_consumption()
        self.purchases = get_purchases()
        self.transfers = get_transfers()
        self.departments = get_departments()
        self.stores = get_stores()
        
        self.errors = []
        self.warnings = []

    def validate_foreign_keys(self):
        """Validate foreign key relationships"""
        print("Validating foreign key relationships...")
        
        # Get all IDs for reference
        medicine_ids = {m['id'] for m in self.medicines}
        patient_ids = {p['id'] for p in self.patients}
        supplier_ids = {s['id'] for s in self.suppliers}
        department_ids = {d['id'] for d in self.departments}
        store_ids = {s['id'] for s in self.stores}
        
        # Validate medicine supplier references
        for medicine in self.medicines:
            if medicine.get('supplier_id') and medicine['supplier_id'] not in supplier_ids:
                self.errors.append(f"Medicine {medicine['id']} references invalid supplier {medicine['supplier_id']}")
        
        # Validate patient department references
        for patient in self.patients:
            if patient.get('department_id') and patient['department_id'] not in department_ids:
                self.errors.append(f"Patient {patient['id']} references invalid department {patient['department_id']}")
        
        # Validate consumption references
        for consumption in self.consumption:
            if consumption.get('patient_id') and consumption['patient_id'] not in patient_ids:
                self.errors.append(f"Consumption {consumption['id']} references invalid patient {consumption['patient_id']}")
            
            if consumption.get('department_id') and consumption['department_id'] not in department_ids:
                self.errors.append(f"Consumption {consumption['id']} references invalid department {consumption['department_id']}")
            
            # Validate medicine references in consumption
            for medicine in consumption.get('medicines', []):
                if medicine.get('medicine_id') and medicine['medicine_id'] not in medicine_ids:
                    self.errors.append(f"Consumption {consumption['id']} references invalid medicine {medicine['medicine_id']}")
        
        # Validate purchase references
        for purchase in self.purchases:
            if purchase.get('supplier_id') and purchase['supplier_id'] not in supplier_ids:
                self.errors.append(f"Purchase {purchase['id']} references invalid supplier {purchase['supplier_id']}")
            
            # Validate medicine references in purchases
            for medicine in purchase.get('medicines', []):
                if medicine.get('medicine_id') and medicine['medicine_id'] not in medicine_ids:
                    self.errors.append(f"Purchase {purchase['id']} references invalid medicine {medicine['medicine_id']}")
        
        # Validate transfer references
        for transfer in self.transfers:
            if transfer.get('source_store_id') and transfer['source_store_id'] not in store_ids:
                self.errors.append(f"Transfer {transfer['id']} references invalid source store {transfer['source_store_id']}")
            
            if transfer.get('destination_store_id') and transfer['destination_store_id'] not in store_ids:
                self.errors.append(f"Transfer {transfer['id']} references invalid destination store {transfer['destination_store_id']}")
            
            # Validate medicine references in transfers
            for medicine in transfer.get('medicines', []):
                if medicine.get('medicine_id') and medicine['medicine_id'] not in medicine_ids:
                    self.errors.append(f"Transfer {transfer['id']} references invalid medicine {medicine['medicine_id']}")

    def validate_date_formats(self):
        """Validate date formats across all tables"""
        print("Validating date formats...")
        
        def check_date_format(date_str: str, record_type: str, record_id: str, field_name: str):
            if date_str:
                try:
                    datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    self.errors.append(f"{record_type} {record_id} has invalid date format in {field_name}: {date_str}")
        
        # Validate medicine expiry dates
        for medicine in self.medicines:
            check_date_format(medicine.get('expiry_date'), 'Medicine', medicine['id'], 'expiry_date')
        
        # Validate patient entry dates
        for patient in self.patients:
            check_date_format(patient.get('date_of_entry'), 'Patient', patient['id'], 'date_of_entry')
        
        # Validate consumption dates
        for consumption in self.consumption:
            check_date_format(consumption.get('date'), 'Consumption', consumption['id'], 'date')
        
        # Validate purchase dates
        for purchase in self.purchases:
            check_date_format(purchase.get('purchase_date'), 'Purchase', purchase['id'], 'purchase_date')
            check_date_format(purchase.get('delivery_date'), 'Purchase', purchase['id'], 'delivery_date')
        
        # Validate transfer dates
        for transfer in self.transfers:
            check_date_format(transfer.get('transfer_date'), 'Transfer', transfer['id'], 'transfer_date')

    def validate_required_fields(self):
        """Validate that required fields are present"""
        print("Validating required fields...")
        
        # Validate medicines
        for medicine in self.medicines:
            if not medicine.get('name'):
                self.errors.append(f"Medicine {medicine['id']} missing required field: name")
            if not medicine.get('supplier_id'):
                self.errors.append(f"Medicine {medicine['id']} missing required field: supplier_id")
        
        # Validate patients
        for patient in self.patients:
            if not patient.get('name'):
                self.errors.append(f"Patient {patient['id']} missing required field: name")
            if not patient.get('age'):
                self.warnings.append(f"Patient {patient['id']} missing age information")
        
        # Validate suppliers
        for supplier in self.suppliers:
            if not supplier.get('name'):
                self.errors.append(f"Supplier {supplier['id']} missing required field: name")
            if not supplier.get('contact_person'):
                self.warnings.append(f"Supplier {supplier['id']} missing contact person")

    def validate_data_consistency(self):
        """Validate logical data consistency"""
        print("Validating data consistency...")
        
        # Check for duplicate IDs within each table
        tables = [
            ('medicines', self.medicines),
            ('patients', self.patients),
            ('suppliers', self.suppliers),
            ('consumption', self.consumption),
            ('purchases', self.purchases),
            ('transfers', self.transfers)
        ]
        
        for table_name, records in tables:
            ids = [record['id'] for record in records]
            if len(ids) != len(set(ids)):
                self.errors.append(f"Duplicate IDs found in {table_name} table")
        
        # Check for reasonable quantities in transfers and purchases
        for transfer in self.transfers:
            for medicine in transfer.get('medicines', []):
                if medicine.get('quantity', 0) <= 0:
                    self.warnings.append(f"Transfer {transfer['id']} has zero or negative quantity for medicine {medicine.get('medicine_id')}")
        
        for purchase in self.purchases:
            for medicine in purchase.get('medicines', []):
                if medicine.get('quantity', 0) <= 0:
                    self.warnings.append(f"Purchase {purchase['id']} has zero or negative quantity for medicine {medicine.get('medicine_id')}")

    def run_validation(self):
        """Run all validation checks"""
        print("=== Starting Data Validation ===\n")
        
        self.validate_foreign_keys()
        self.validate_date_formats()
        self.validate_required_fields()
        self.validate_data_consistency()
        
        print(f"\n=== Validation Results ===")
        print(f"Errors found: {len(self.errors)}")
        print(f"Warnings found: {len(self.warnings)}")
        
        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  ❌ {error}")
        
        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ All data validation checks passed!")
        
        return len(self.errors), len(self.warnings)

if __name__ == "__main__":
    validator = DataValidator()
    validator.run_validation()
