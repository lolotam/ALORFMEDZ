"""
Enhanced Sample Data Generator for Hospital Pharmacy Management System
Creates 5 records for each section and provides backup with CSV exports in ZIP format
"""

import json
import os
import csv
import zipfile
import shutil
from datetime import datetime, timedelta
import random
import tempfile
from app.utils.database import DATA_DIR, DB_FILES, generate_id

class EnhancedSampleDataGenerator:
    def __init__(self):
        self.backup_dir = None

    def create_backup_zip(self):
        """Create a comprehensive backup ZIP with all data in both JSON and CSV formats"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'pharmacy_data_backup_{timestamp}.zip'
        zip_path = os.path.join(DATA_DIR, zip_filename)

        # Create temporary directory for CSV files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Export all data to CSV files
            self.export_all_to_csv(temp_dir)

            # Create ZIP file
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add JSON files
                for data_type, file_path in DB_FILES.items():
                    if os.path.exists(file_path):
                        zipf.write(file_path, f'json/{data_type}.json')

                # Add CSV files
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.csv'):
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, f'csv/{file}')

                # Add backup metadata
                metadata = {
                    'backup_date': datetime.now().isoformat(),
                    'backup_type': 'enhanced_sample_data',
                    'description': 'Complete data backup with JSON and CSV formats',
                    'version': '2.0.0',
                    'files_included': list(DB_FILES.keys())
                }
                zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2))

        return zip_path

    def export_all_to_csv(self, output_dir):
        """Export all data to CSV files"""
        csv_exporters = {
            'medicines': self.export_medicines_csv,
            'patients': self.export_patients_csv,
            'suppliers': self.export_suppliers_csv,
            'departments': self.export_departments_csv,
            'doctors': self.export_doctors_csv,
            'stores': self.export_stores_csv,
            'purchases': self.export_purchases_csv,
            'consumption': self.export_consumption_csv,
            'transfers': self.export_transfers_csv,
            'users': self.export_users_csv,
            'history': self.export_history_csv
        }

        for data_type, exporter in csv_exporters.items():
            try:
                file_path = DB_FILES.get(data_type)
                if file_path and os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    csv_path = os.path.join(output_dir, f'{data_type}.csv')
                    exporter(data, csv_path)
                    print(f"Exported {data_type} to CSV: {len(data)} records")
            except Exception as e:
                print(f"Error exporting {data_type} to CSV: {str(e)}")

    def export_medicines_csv(self, data, csv_path):
        """Export medicines data to CSV"""
        if not data:
            return

        fieldnames = ['id', 'name', 'supplier_id', 'category', 'form_dosage', 'strength',
                     'low_stock_limit', 'unit_price', 'notes', 'created_at']

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in data:
                # Only write fields that exist in fieldnames
                filtered_record = {k: v for k, v in record.items() if k in fieldnames}
                writer.writerow(filtered_record)

    def export_patients_csv(self, data, csv_path):
        """Export patients data to CSV"""
        if not data:
            return

        fieldnames = ['id', 'name', 'age', 'gender', 'phone', 'address',
                     'medical_history', 'allergies', 'created_at']

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in data:
                filtered_record = {k: v for k, v in record.items() if k in fieldnames}
                writer.writerow(filtered_record)

    def export_suppliers_csv(self, data, csv_path):
        """Export suppliers data to CSV"""
        if not data:
            return

        fieldnames = ['id', 'name', 'contact_person', 'phone', 'email',
                     'address', 'city', 'created_at']

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in data:
                filtered_record = {k: v for k, v in record.items() if k in fieldnames}
                writer.writerow(filtered_record)

    def export_departments_csv(self, data, csv_path):
        """Export departments data to CSV"""
        if not data:
            return

        fieldnames = ['id', 'name', 'description', 'responsible_person',
                     'telephone', 'notes', 'created_at']

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in data:
                filtered_record = {k: v for k, v in record.items() if k in fieldnames}
                writer.writerow(filtered_record)

    def export_doctors_csv(self, data, csv_path):
        """Export doctors data to CSV"""
        if not data:
            return

        fieldnames = ['id', 'dr_name', 'gender', 'nationality', 'department_id', 'specialist',
                     'position', 'type', 'mobile_no', 'email', 'license_number', 'note',
                     'created_at', 'updated_at']

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in data:
                filtered_record = {k: v for k, v in record.items() if k in fieldnames}
                writer.writerow(filtered_record)

    def export_stores_csv(self, data, csv_path):
        """Export stores data to CSV"""
        if not data:
            return

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Store ID', 'Store Name', 'Department ID', 'Location',
                           'Medicine ID', 'Medicine Stock', 'Created At'])

            for store in data:
                inventory = store.get('inventory', {})
                if inventory:
                    for med_id, stock in inventory.items():
                        writer.writerow([
                            store.get('id', ''),
                            store.get('name', ''),
                            store.get('department_id', ''),
                            store.get('location', ''),
                            med_id,
                            stock,
                            store.get('created_at', '')
                        ])
                else:
                    writer.writerow([
                        store.get('id', ''),
                        store.get('name', ''),
                        store.get('department_id', ''),
                        store.get('location', ''),
                        '', '',
                        store.get('created_at', '')
                    ])

    def export_purchases_csv(self, data, csv_path):
        """Export purchases data to CSV"""
        if not data:
            return

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Purchase ID', 'Supplier ID', 'Invoice Number', 'Purchase Date',
                           'Medicine ID', 'Quantity', 'Unit Price', 'Total Price',
                           'Status', 'Notes', 'Created At'])

            for purchase in data:
                medicines = purchase.get('medicines', [])
                if medicines:
                    for med in medicines:
                        writer.writerow([
                            purchase.get('id', ''),
                            purchase.get('supplier_id', ''),
                            purchase.get('invoice_number', ''),
                            purchase.get('purchase_date', ''),
                            med.get('medicine_id', ''),
                            med.get('quantity', ''),
                            med.get('unit_price', ''),
                            med.get('total_price', ''),
                            purchase.get('status', ''),
                            purchase.get('notes', ''),
                            purchase.get('created_at', '')
                        ])
                else:
                    writer.writerow([
                        purchase.get('id', ''),
                        purchase.get('supplier_id', ''),
                        purchase.get('invoice_number', ''),
                        purchase.get('purchase_date', ''),
                        '', '', '', '',
                        purchase.get('status', ''),
                        purchase.get('notes', ''),
                        purchase.get('created_at', '')
                    ])

    def export_consumption_csv(self, data, csv_path):
        """Export consumption data to CSV"""
        if not data:
            return

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Consumption ID', 'Patient ID', 'Date', 'Medicine ID',
                           'Quantity', 'Prescribed By', 'Notes', 'Created At'])

            for consumption in data:
                medicines = consumption.get('medicines', [])
                if medicines:
                    for med in medicines:
                        writer.writerow([
                            consumption.get('id', ''),
                            consumption.get('patient_id', ''),
                            consumption.get('date', ''),
                            med.get('medicine_id', ''),
                            med.get('quantity', ''),
                            consumption.get('prescribed_by', ''),
                            consumption.get('notes', ''),
                            consumption.get('created_at', '')
                        ])
                else:
                    writer.writerow([
                        consumption.get('id', ''),
                        consumption.get('patient_id', ''),
                        consumption.get('date', ''),
                        '', '',
                        consumption.get('prescribed_by', ''),
                        consumption.get('notes', ''),
                        consumption.get('created_at', '')
                    ])

    def export_transfers_csv(self, data, csv_path):
        """Export transfers data to CSV"""
        if not data:
            return

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Transfer ID', 'Source Store ID', 'Destination Store ID',
                           'Medicine ID', 'Quantity', 'Transfer Date', 'Status',
                           'Notes', 'Created At'])

            for transfer in data:
                medicines = transfer.get('medicines', [])
                if medicines:
                    for med in medicines:
                        writer.writerow([
                            transfer.get('id', ''),
                            transfer.get('source_store_id', ''),
                            transfer.get('destination_store_id', ''),
                            med.get('medicine_id', ''),
                            med.get('quantity', ''),
                            transfer.get('transfer_date', ''),
                            transfer.get('status', ''),
                            transfer.get('notes', ''),
                            transfer.get('created_at', '')
                        ])
                else:
                    writer.writerow([
                        transfer.get('id', ''),
                        transfer.get('source_store_id', ''),
                        transfer.get('destination_store_id', ''),
                        '', '',
                        transfer.get('transfer_date', ''),
                        transfer.get('status', ''),
                        transfer.get('notes', ''),
                        transfer.get('created_at', '')
                    ])

    def export_users_csv(self, data, csv_path):
        """Export users data to CSV"""
        if not data:
            return

        fieldnames = ['id', 'username', 'role', 'name', 'email',
                     'department_id', 'created_at']

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in data:
                # Exclude password for security
                filtered_record = {k: v for k, v in record.items() if k in fieldnames}
                writer.writerow(filtered_record)

    def export_history_csv(self, data, csv_path):
        """Export history data to CSV"""
        if not data:
            return

        fieldnames = ['id', 'action', 'entity_type', 'entity_id', 'user_id',
                     'timestamp', 'details']

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in data:
                # Convert details dict to string if needed
                if 'details' in record and isinstance(record['details'], dict):
                    record['details'] = json.dumps(record['details'])
                filtered_record = {k: v for k, v in record.items() if k in fieldnames}
                writer.writerow(filtered_record)

    def safe_backup_and_save(self, data_type, data):
        """Safely backup existing data and save new data"""
        file_path = DB_FILES.get(data_type)
        if not file_path:
            return

        # Create backup if file exists
        if os.path.exists(file_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = file_path.replace('.json', f'_backup_{timestamp}.json')

            # Ensure backup doesn't already exist
            counter = 1
            while os.path.exists(backup_path):
                backup_path = file_path.replace('.json', f'_backup_{timestamp}_{counter}.json')
                counter += 1

            try:
                shutil.copy2(file_path, backup_path)
                print(f"Backed up existing {data_type}.json to {os.path.basename(backup_path)}")
            except Exception as e:
                print(f"Warning: Could not backup {data_type}.json: {str(e)}")

        # Save new data
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Generated {len(data)} {data_type} records")
        except Exception as e:
            print(f"Error saving {data_type}.json: {str(e)}")

    def generate_sample_data(self):
        """Generate sample data with 5 records for each section"""
        print("Generating enhanced sample data (5 records per section)...")

        # Generate sample data
        suppliers = self.generate_suppliers(5)
        departments = self.generate_departments(5)
        doctors = self.generate_doctors(5, departments)
        medicines = self.generate_medicines(5, suppliers)
        stores = self.generate_stores(departments)
        patients = self.generate_patients(5)
        purchases = self.generate_purchases(5, medicines, suppliers)
        consumption = self.generate_consumption(5, patients, medicines)
        transfers = self.generate_transfers(5, stores, medicines)
        users = self.generate_users()
        history = []

        # Update inventories
        self.update_store_inventories(stores, purchases)
        self.update_inventories_after_consumption(stores, consumption)
        self.update_inventories_after_transfers(stores, transfers)

        # Save all data
        data_collections = {
            'suppliers': suppliers,
            'departments': departments,
            'doctors': doctors,
            'medicines': medicines,
            'stores': stores,
            'patients': patients,
            'purchases': purchases,
            'consumption': consumption,
            'transfers': transfers,
            'users': users,
            'history': history
        }

        for data_type, data in data_collections.items():
            self.safe_backup_and_save(data_type, data)

        # Create comprehensive backup ZIP
        zip_path = self.create_backup_zip()

        print("\n=== Enhanced Sample Data Generation Summary ===")
        for data_type, data in data_collections.items():
            print(f"- {len(data)} {data_type} records")
        print(f"\nBackup ZIP created: {os.path.basename(zip_path)}")

        return data_collections, zip_path

    def generate_suppliers(self, count=5):
        """Generate supplier records"""
        suppliers = []
        supplier_names = [
            "MediCorp Pharmaceuticals", "HealthSupply Solutions", "Global Pharma Trading",
            "Medical Distributors Ltd", "BioMed Supply Chain"
        ]

        for i in range(count):
            name = supplier_names[i] if i < len(supplier_names) else f"Supplier {i+1}"
            supplier = {
                'id': f"{i+1:02d}",
                'name': name,
                'contact_person': f"Contact Person {i+1}",
                'phone': f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                'email': f"contact{i+1}@{name.lower().replace(' ', '').replace('.', '')}.com",
                'address': f"{random.randint(100, 9999)} Medical Plaza, Suite {random.randint(100, 999)}",
                'city': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
                'created_at': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()
            }
            suppliers.append(supplier)

        return suppliers

    def generate_departments(self, count=5):
        """Generate department records"""
        departments = [
            {'id': '01', 'name': 'Main Pharmacy', 'description': 'Central pharmacy department', 'responsible_person': 'Chief Pharmacist', 'telephone': '+1-555-PHARM', 'notes': 'Main distribution center'},
            {'id': '02', 'name': 'Emergency Department', 'description': 'Emergency medicine and trauma care', 'responsible_person': 'ER Director', 'telephone': '+1-555-EMERG', 'notes': 'Critical care medications'},
            {'id': '03', 'name': 'Intensive Care Unit', 'description': 'Critical care and life support', 'responsible_person': 'ICU Manager', 'telephone': '+1-555-ICU01', 'notes': 'Life-saving medications'},
            {'id': '04', 'name': 'Cardiology', 'description': 'Heart and cardiovascular care', 'responsible_person': 'Cardiology Head', 'telephone': '+1-555-HEART', 'notes': 'Cardiac medications'},
            {'id': '05', 'name': 'Oncology', 'description': 'Cancer treatment and chemotherapy', 'responsible_person': 'Oncology Director', 'telephone': '+1-555-ONCOL', 'notes': 'Chemotherapy drugs'}
        ]

        for dept in departments[:count]:
            dept['created_at'] = (datetime.now() - timedelta(days=random.randint(100, 500))).isoformat()

        return departments[:count]

    def generate_doctors(self, count=5, departments=None):
        """Generate doctor records"""
        doctors = []
        doctor_names = [
            "Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. Emma Wilson",
            "Dr. David Rodriguez", "Dr. Lisa Anderson"
        ]
        specializations = [
            "Emergency Medicine", "Cardiology", "Internal Medicine",
            "Oncology", "Critical Care"
        ]
        qualifications = [
            "MD, FACEP", "MD, FACC", "MD, FACP",
            "MD, PhD", "MD, FCCM"
        ]
        nationalities = ["American", "British", "Canadian", "Australian", "Indian"]

        for i in range(count):
            # Assign to department if available
            department_id = departments[i % len(departments)]['id'] if departments else f"{i+1:02d}"

            doctor = {
                'id': f"{i+1:02d}",
                'dr_name': doctor_names[i] if i < len(doctor_names) else f"Dr. Doctor {i+1}",
                'gender': random.choice(['male', 'female']),
                'nationality': nationalities[i] if i < len(nationalities) else 'American',
                'department_id': department_id,
                'specialist': specializations[i] if i < len(specializations) else 'General Medicine',
                'position': qualifications[i] if i < len(qualifications) else 'MD',
                'type': random.choice(['employee', 'visitor']),
                'mobile_no': f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                'email': f"doctor{i+1}@hospital.com",
                'license_number': f"MD{random.randint(10000, 99999)}",
                'note': f"Experienced {specializations[i] if i < len(specializations) else 'General Medicine'} specialist",
                'created_at': (datetime.now() - timedelta(days=random.randint(100, 1000))).isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            doctors.append(doctor)

        return doctors

    def generate_medicines(self, count=5, suppliers=None):
        """Generate medicine records"""
        medicines = []
        medicine_names = ['Paracetamol', 'Ibuprofen', 'Amoxicillin', 'Metformin', 'Lisinopril']
        categories = ['Analgesics', 'Anti-inflammatory', 'Antibiotics', 'Diabetes', 'Cardiovascular']

        for i in range(count):
            medicine = {
                'id': f"{i+1:02d}",
                'name': medicine_names[i] if i < len(medicine_names) else f"Medicine {i+1}",
                'supplier_id': suppliers[i % len(suppliers)]['id'] if suppliers else '01',
                'category': categories[i] if i < len(categories) else 'General',
                'form_dosage': random.choice(['Tablet 500mg', 'Capsule 250mg', 'Injection 10ml', 'Syrup 100ml']),
                'strength': f"{random.randint(5, 500)}{random.choice(['mg', 'ml', 'units'])}",
                'low_stock_limit': random.randint(10, 50),
                'unit_price': round(random.uniform(0.5, 50.0), 2),
                'notes': f"Standard {categories[i] if i < len(categories) else 'general'} medication",
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 200))).isoformat()
            }
            medicines.append(medicine)

        return medicines

    def generate_stores(self, departments):
        """Generate stores for departments"""
        stores = []
        for dept in departments:
            store = {
                'id': dept['id'],
                'name': f"{dept['name']} Store",
                'department_id': dept['id'],
                'location': f"Building {random.choice(['A', 'B', 'C'])}, Floor {random.randint(1, 5)}",
                'description': f"Store for {dept['name']}",
                'inventory': {},
                'created_at': dept['created_at']
            }
            stores.append(store)

        return stores

    def generate_patients(self, count=5):
        """Generate patient records"""
        patients = []
        first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones']
        # Department IDs excluding Main Pharmacy (01)
        department_ids = ['02', '03', '04', '05']

        for i in range(count):
            patient = {
                'id': f"{i+1:02d}",
                'name': f"{first_names[i]} {last_names[i]}",
                'age': random.randint(25, 75),
                'gender': random.choice(['Male', 'Female']),
                'phone': f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                'address': f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine'])} Street",
                'medical_history': random.choice(['Diabetes', 'Hypertension', 'Asthma', 'Heart Disease', 'None']),
                'allergies': random.choice(['None', 'Penicillin', 'Aspirin', 'Latex']),
                'file_no': f"PAT-{datetime.now().year}-{i+1:04d}",
                'department_id': random.choice(department_ids),
                'notes': random.choice([
                    'Regular checkup required',
                    'Follow-up appointment scheduled',
                    'Requires special attention',
                    'Chronic condition monitoring',
                    'Post-operative care'
                ]),
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat()
            }
            patients.append(patient)

        return patients

    def generate_purchases(self, count=5, medicines=None, suppliers=None):
        """Generate purchase records"""
        purchases = []
        receiver_names = ['John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis', 'David Wilson']

        for i in range(count):
            supplier = suppliers[i % len(suppliers)] if suppliers else {'id': '01'}
            selected_medicines = [medicines[i]] if medicines and i < len(medicines) else []

            purchase_medicines = []
            total_amount = 0

            for medicine in selected_medicines:
                quantity = random.randint(100, 500)
                unit_price = medicine.get('unit_price', 10.0)
                total_price = quantity * unit_price
                total_amount += total_price

                purchase_medicines.append({
                    'medicine_id': medicine['id'],
                    'quantity': quantity
                })

            purchase_date = datetime.now() - timedelta(days=random.randint(1, 60))
            # Delivery date is 1-7 days after purchase date
            delivery_date = purchase_date + timedelta(days=random.randint(1, 7))

            purchase = {
                'id': f"{i+1:02d}",
                'supplier_id': supplier['id'],
                'invoice_number': f"INV-{random.randint(1000, 9999)}",
                'date': purchase_date.isoformat()[:10],
                'medicines': purchase_medicines,
                'purchaser_name': f"Purchaser {i+1}",
                'status': 'delivered',
                'delivery_date': delivery_date.isoformat()[:10],
                'received_by': random.choice(receiver_names),
                'notes': f"Purchase from {supplier.get('name', 'Supplier')}",
                'created_at': purchase_date.isoformat()
            }
            purchases.append(purchase)

        return purchases

    def generate_consumption(self, count=5, patients=None, medicines=None):
        """Generate consumption records"""
        consumption_records = []
        # Department IDs excluding Main Pharmacy (01)
        department_ids = ['02', '03', '04', '05']

        for i in range(count):
            patient = patients[i] if patients and i < len(patients) else {'id': f"{i+1:02d}"}
            selected_medicine = medicines[i] if medicines and i < len(medicines) else {'id': f"{i+1:02d}"}

            consumption_medicines = [{
                'medicine_id': selected_medicine['id'],
                'quantity': random.randint(1, 10)
            }]

            # Use patient's department if available, otherwise random
            department_id = patient.get('department_id', random.choice(department_ids))

            consumption = {
                'id': f"{i+1:02d}",
                'patient_id': patient['id'],
                'department_id': department_id,
                'date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()[:10],
                'medicines': consumption_medicines,
                'prescribed_by': f"Dr. {random.choice(['Smith', 'Johnson', 'Williams'])}",
                'notes': f"Prescription for {patient.get('name', 'Patient')}",
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
            consumption_records.append(consumption)

        return consumption_records

    def generate_transfers(self, count=5, stores=None, medicines=None):
        """Generate transfer records"""
        transfers = []

        if not stores or len(stores) < 2:
            return transfers

        main_store = stores[0]
        other_stores = stores[1:] if len(stores) > 1 else []

        for i in range(min(count, len(other_stores))):
            dest_store = other_stores[i % len(other_stores)]
            selected_medicine = medicines[i] if medicines and i < len(medicines) else {'id': f"{i+1:02d}"}

            transfer_medicines = [{
                'medicine_id': selected_medicine['id'],
                'quantity': random.randint(5, 50)
            }]

            transfer = {
                'id': f"{i+1:02d}",
                'source_store_id': main_store['id'],
                'destination_store_id': dest_store['id'],
                'medicines': transfer_medicines,
                'transfer_date': (datetime.now() - timedelta(days=random.randint(1, 20))).isoformat()[:10],
                'notes': f"Transfer to {dest_store['name']}",
                'status': 'completed',
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 20))).isoformat()
            }
            transfers.append(transfer)

        return transfers

    def generate_users(self):
        """Generate user accounts"""
        users = [
            {
                'id': '01',
                'username': 'admin',
                'password': '@Xx123456789xX@',
                'role': 'admin',
                'name': 'System Administrator',
                'email': 'admin@hospital.com',
                'department_id': None,
                'created_at': datetime.now().isoformat()
            },
            {
                'id': '02',
                'username': 'pharmacy',
                'password': 'pharmacy123',
                'role': 'department_user',
                'name': 'Pharmacy User',
                'email': 'pharmacy@hospital.com',
                'department_id': '01',
                'created_at': datetime.now().isoformat()
            }
        ]

        return users

    def update_store_inventories(self, stores, purchases):
        """Update store inventories based on purchases"""
        main_store = next((s for s in stores if s['id'] == '01'), None)
        if not main_store:
            return

        for purchase in purchases:
            for medicine in purchase['medicines']:
                medicine_id = medicine['medicine_id']
                quantity = medicine['quantity']

                if medicine_id not in main_store['inventory']:
                    main_store['inventory'][medicine_id] = 0
                main_store['inventory'][medicine_id] += quantity

    def update_inventories_after_consumption(self, stores, consumption_records):
        """Update store inventories after consumption"""
        main_store = next((s for s in stores if s['id'] == '01'), None)
        if not main_store:
            return

        for consumption in consumption_records:
            for medicine in consumption['medicines']:
                medicine_id = medicine['medicine_id']
                quantity = medicine['quantity']

                if medicine_id in main_store['inventory']:
                    main_store['inventory'][medicine_id] = max(0, main_store['inventory'][medicine_id] - quantity)

    def update_inventories_after_transfers(self, stores, transfers):
        """Update store inventories after transfers"""
        store_dict = {s['id']: s for s in stores}

        for transfer in transfers:
            source_store = store_dict.get(transfer['source_store_id'])
            dest_store = store_dict.get(transfer['destination_store_id'])

            if source_store and dest_store:
                for medicine in transfer['medicines']:
                    medicine_id = medicine['medicine_id']
                    quantity = medicine['quantity']

                    # Deduct from source
                    if medicine_id in source_store['inventory']:
                        source_store['inventory'][medicine_id] = max(0, source_store['inventory'][medicine_id] - quantity)

                    # Add to destination
                    if medicine_id not in dest_store['inventory']:
                        dest_store['inventory'][medicine_id] = 0
                    dest_store['inventory'][medicine_id] += quantity

def generate_enhanced_sample_data():
    """Main function to generate enhanced sample data"""
    generator = EnhancedSampleDataGenerator()
    return generator.generate_sample_data()

if __name__ == "__main__":
    generate_enhanced_sample_data()