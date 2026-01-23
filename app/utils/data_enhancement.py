"""
Data Enhancement Utility
Fills empty fields across all database tables with realistic sample data
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List
from app.utils.database import (
    get_medicines, save_data, get_patients, get_suppliers, 
    get_consumption, get_purchases, get_transfers, get_departments
)

class DataEnhancer:
    def __init__(self):
        self.departments = get_departments()
        self.medicines = get_medicines()
        self.patients = get_patients()
        self.suppliers = get_suppliers()
        
        # Medical data for realistic enhancement
        self.batch_prefixes = ['BATCH', 'LOT', 'MFG', 'PRD', 'MED']
        self.barcode_prefixes = ['123456789', '987654321', '456789123', '789123456', '321654987']
        
        self.medical_notes = [
            "For pain relief and fever reduction",
            "Anti-inflammatory medication",
            "Antibiotic for bacterial infections",
            "For cardiovascular conditions",
            "Respiratory medication",
            "Gastrointestinal treatment",
            "Neurological medication",
            "Dermatological treatment",
            "Endocrine system medication",
            "Immunosuppressive therapy"
        ]
        
        self.patient_notes = [
            "Regular follow-up required",
            "Monitor for side effects",
            "Chronic condition management",
            "Post-operative care",
            "Emergency treatment",
            "Routine medication",
            "Specialist consultation needed",
            "Stable condition",
            "Requires close monitoring",
            "Outpatient treatment"
        ]
        
        self.supplier_notes = [
            "Preferred supplier for emergency medicines",
            "Reliable delivery schedule",
            "Competitive pricing for bulk orders",
            "Specialized in rare medications",
            "Fast delivery service",
            "Quality certified supplier",
            "Long-term partnership",
            "Regional distributor",
            "International pharmaceutical supplier",
            "Local medical equipment provider"
        ]

    def generate_expiry_date(self) -> str:
        """Generate realistic expiry date (6 months to 3 years from now)"""
        days_ahead = random.randint(180, 1095)  # 6 months to 3 years
        expiry = datetime.now() + timedelta(days=days_ahead)
        return expiry.strftime('%Y-%m-%d')

    def generate_batch_number(self) -> str:
        """Generate realistic batch number"""
        prefix = random.choice(self.batch_prefixes)
        number = random.randint(1000, 9999)
        year = random.choice(['24', '25', '26'])
        return f"{prefix}{year}{number}"

    def generate_barcode(self) -> str:
        """Generate realistic barcode number"""
        prefix = random.choice(self.barcode_prefixes)
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        return f"{prefix}{suffix}"

    def enhance_medicines(self):
        """Fill empty fields in medicines table"""
        print("Enhancing medicines data...")
        updated_count = 0
        
        for medicine in self.medicines:
            updated = False
            
            # Fill expiry_date if null
            if medicine.get('expiry_date') is None:
                medicine['expiry_date'] = self.generate_expiry_date()
                updated = True
            
            # Fill batch_number if null
            if medicine.get('batch_number') is None:
                medicine['batch_number'] = self.generate_batch_number()
                updated = True
            
            # Fill barcode_number if null
            if medicine.get('barcode_number') is None:
                medicine['barcode_number'] = self.generate_barcode()
                updated = True
            
            # Enhance notes if empty or generic
            if not medicine.get('notes') or medicine.get('notes') in ['', 'N/A']:
                medicine['notes'] = random.choice(self.medical_notes)
                updated = True
            
            if updated:
                medicine['updated_at'] = datetime.now().isoformat()
                updated_count += 1
        
        if updated_count > 0:
            save_data('medicines', self.medicines)
            print(f"Enhanced {updated_count} medicine records")
        return updated_count

    def enhance_patients(self):
        """Fill empty fields in patients table"""
        print("Enhancing patients data...")
        updated_count = 0
        
        for patient in self.patients:
            updated = False
            
            # Fill department_id if missing
            if not patient.get('department_id'):
                # Assign random department
                dept = random.choice(self.departments)
                patient['department_id'] = dept['id']
                updated = True
            
            # Fill notes if missing
            if not patient.get('notes'):
                patient['notes'] = random.choice(self.patient_notes)
                updated = True
            
            # Add file_no if missing
            if not patient.get('file_no'):
                patient['file_no'] = f"P{random.randint(1000, 9999)}"
                updated = True
            
            # Add date_of_entry if missing
            if not patient.get('date_of_entry'):
                # Random date within last 6 months
                days_ago = random.randint(1, 180)
                entry_date = datetime.now() - timedelta(days=days_ago)
                patient['date_of_entry'] = entry_date.strftime('%Y-%m-%d')
                updated = True
            
            if updated:
                patient['updated_at'] = datetime.now().isoformat()
                updated_count += 1
        
        if updated_count > 0:
            save_data('patients', self.patients)
            print(f"Enhanced {updated_count} patient records")
        return updated_count

    def enhance_suppliers(self):
        """Fill empty fields in suppliers table"""
        print("Enhancing suppliers data...")
        updated_count = 0
        
        for supplier in self.suppliers:
            updated = False
            
            # Fill empty notes
            if not supplier.get('notes') or supplier.get('notes') == '':
                supplier['notes'] = random.choice(self.supplier_notes)
                updated = True
            
            # Enhance contact person if generic
            if supplier.get('contact_person', '').startswith('Contact Person'):
                names = ['John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis', 
                        'David Wilson', 'Lisa Anderson', 'Robert Taylor', 'Jennifer Martinez']
                supplier['contact_person'] = random.choice(names)
                updated = True
            
            # Add website if missing
            if not supplier.get('website'):
                company_name = supplier['name'].lower().replace(' ', '').replace('.', '')
                supplier['website'] = f"www.{company_name}.com"
                updated = True
            
            # Add tax_id if missing
            if not supplier.get('tax_id'):
                supplier['tax_id'] = f"TAX{random.randint(100000, 999999)}"
                updated = True
            
            if updated:
                supplier['updated_at'] = datetime.now().isoformat()
                updated_count += 1
        
        if updated_count > 0:
            save_data('suppliers', self.suppliers)
            print(f"Enhanced {updated_count} supplier records")
        return updated_count

    def enhance_consumption_records(self):
        """Fill missing fields in consumption records"""
        print("Enhancing consumption records...")
        consumption_records = get_consumption()
        updated_count = 0

        for record in consumption_records:
            updated = False

            # Fill department_id if missing
            if not record.get('department_id'):
                # Get department from patient if available
                patient = next((p for p in self.patients if p['id'] == record.get('patient_id')), None)
                if patient and patient.get('department_id'):
                    record['department_id'] = patient['department_id']
                else:
                    # Assign random department
                    dept = random.choice(self.departments)
                    record['department_id'] = dept['id']
                updated = True

            # Fill prescribed_by if missing
            if not record.get('prescribed_by'):
                doctors = ['Dr. Smith', 'Dr. Johnson', 'Dr. Williams', 'Dr. Brown', 'Dr. Davis',
                          'Dr. Miller', 'Dr. Wilson', 'Dr. Moore', 'Dr. Taylor', 'Dr. Anderson']
                record['prescribed_by'] = random.choice(doctors)
                updated = True

            # Fill notes if missing
            if not record.get('notes'):
                patient = next((p for p in self.patients if p['id'] == record.get('patient_id')), None)
                if patient:
                    record['notes'] = f"Medication for {patient['name']}"
                else:
                    record['notes'] = "Standard medication dispensing"
                updated = True

            if updated:
                record['updated_at'] = datetime.now().isoformat()
                updated_count += 1

        if updated_count > 0:
            save_data('consumption', consumption_records)
            print(f"Enhanced {updated_count} consumption records")
        return updated_count

    def enhance_purchase_records(self):
        """Fill missing fields in purchase records"""
        print("Enhancing purchase records...")
        purchase_records = get_purchases()
        updated_count = 0

        for record in purchase_records:
            updated = False

            # Fill delivery_date if missing
            if not record.get('delivery_date') and record.get('purchase_date'):
                # Delivery usually 1-7 days after purchase
                try:
                    purchase_date = datetime.strptime(record['purchase_date'], '%Y-%m-%d')
                    delivery_days = random.randint(1, 7)
                    delivery_date = purchase_date + timedelta(days=delivery_days)
                    record['delivery_date'] = delivery_date.strftime('%Y-%m-%d')
                    updated = True
                except (ValueError, KeyError):
                    # If purchase_date is invalid, set delivery to recent date
                    delivery_date = datetime.now() - timedelta(days=random.randint(1, 30))
                    record['delivery_date'] = delivery_date.strftime('%Y-%m-%d')
                    updated = True

            # Fill payment_method if missing
            if not record.get('payment_method'):
                methods = ['Bank Transfer', 'Credit Card', 'Cash', 'Check', 'Net 30']
                record['payment_method'] = random.choice(methods)
                updated = True

            # Fill notes if missing
            if not record.get('notes'):
                supplier = next((s for s in self.suppliers if s['id'] == record.get('supplier_id')), None)
                if supplier:
                    record['notes'] = f"Purchase from {supplier['name']}"
                else:
                    record['notes'] = "Standard medicine procurement"
                updated = True

            # Fill received_by if missing
            if not record.get('received_by'):
                staff = ['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson', 'Tom Brown']
                record['received_by'] = random.choice(staff)
                updated = True

            if updated:
                record['updated_at'] = datetime.now().isoformat()
                updated_count += 1

        if updated_count > 0:
            save_data('purchases', purchase_records)
            print(f"Enhanced {updated_count} purchase records")
        return updated_count

    def enhance_transfer_records(self):
        """Fill missing fields in transfer records"""
        print("Enhancing transfer records...")
        transfer_records = get_transfers()
        updated_count = 0

        for record in transfer_records:
            updated = False

            # Fill transfer_date if missing
            if not record.get('transfer_date'):
                # Random date within last 30 days
                days_ago = random.randint(1, 30)
                transfer_date = datetime.now() - timedelta(days=days_ago)
                record['transfer_date'] = transfer_date.strftime('%Y-%m-%d')
                updated = True

            # Fill requested_by if missing
            if not record.get('requested_by'):
                staff = ['Dr. Smith', 'Nurse Johnson', 'Pharmacist Brown', 'Dr. Wilson', 'Nurse Davis']
                record['requested_by'] = random.choice(staff)
                updated = True

            # Fill approved_by if missing
            if not record.get('approved_by'):
                managers = ['Pharmacy Manager', 'Department Head', 'Chief Pharmacist', 'Medical Director']
                record['approved_by'] = random.choice(managers)
                updated = True

            if updated:
                record['updated_at'] = datetime.now().isoformat()
                updated_count += 1

        if updated_count > 0:
            save_data('transfers', transfer_records)
            print(f"Enhanced {updated_count} transfer records")
        return updated_count

    def run_all_enhancements(self):
        """Run all data enhancement operations"""
        print("=== Starting Data Enhancement Process ===\n")

        results = {
            'medicines': self.enhance_medicines(),
            'patients': self.enhance_patients(),
            'suppliers': self.enhance_suppliers(),
            'consumption': self.enhance_consumption_records(),
            'purchases': self.enhance_purchase_records(),
            'transfers': self.enhance_transfer_records()
        }

        print(f"\n=== Data Enhancement Summary ===")
        total_enhanced = sum(results.values())
        for table, count in results.items():
            print(f"{table.capitalize()}: {count} records enhanced")
        print(f"Total records enhanced: {total_enhanced}")

        return results

if __name__ == "__main__":
    enhancer = DataEnhancer()
    enhancer.run_all_enhancements()
