"""
Sample Data Generator for Hospital Pharmacy Management System
Creates comprehensive sample data for testing and demonstration
"""

import json
import os
from datetime import datetime, timedelta
import random
from utils.database import DATA_DIR, DB_FILES, generate_id

def generate_sample_data():
    """Generate comprehensive sample data for the system"""
    
    # Sample data collections
    sample_data = {
        'suppliers': generate_suppliers(),
        'departments': generate_departments(),
        'medicines': [],  # Will be generated after suppliers
        'stores': [],     # Will be generated after departments
        'patients': generate_patients(),
        'purchases': [],  # Will be generated after medicines
        'consumption': [],  # Will be generated after patients and medicines
        'transfers': [],   # Will be generated after stores and medicines
        'users': generate_users(),
        'history': []
    }
    
    # Generate medicines (depends on suppliers)
    sample_data['medicines'] = generate_medicines(sample_data['suppliers'])
    
    # Generate stores (depends on departments)
    sample_data['stores'] = generate_stores(sample_data['departments'])
    
    # Generate purchases (depends on medicines and suppliers)
    sample_data['purchases'] = generate_purchases(sample_data['medicines'], sample_data['suppliers'])
    
    # Update store inventories based on purchases
    update_store_inventories(sample_data['stores'], sample_data['purchases'])
    
    # Generate consumption (depends on patients and medicines)
    sample_data['consumption'] = generate_consumption(sample_data['patients'], sample_data['medicines'], sample_data['stores'])
    
    # Update inventories after consumption
    update_inventories_after_consumption(sample_data['stores'], sample_data['consumption'])
    
    # Generate transfers (depends on stores and medicines)
    sample_data['transfers'] = generate_transfers(sample_data['stores'], sample_data['medicines'])
    
    # Update inventories after transfers
    update_inventories_after_transfers(sample_data['stores'], sample_data['transfers'])
    
    return sample_data

def generate_suppliers():
    """Generate 10 supplier records"""
    suppliers = []
    supplier_names = [
        "PharmaCorp International", "MediSupply Ltd", "HealthCare Distributors",
        "Global Pharma Solutions", "Medical Supplies Inc", "BioMed Partners",
        "Therapeutic Distributors", "Wellness Supply Chain", "MedTech Suppliers",
        "Advanced Pharmaceuticals"
    ]
    
    for i, name in enumerate(supplier_names):
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

def generate_departments():
    """Generate 10 departments plus main pharmacy"""
    departments = [
        {'id': '01', 'name': 'Main Pharmacy', 'description': 'Central pharmacy department'},
        {'id': '02', 'name': 'Emergency Department', 'description': 'Emergency medicine and trauma care'},
        {'id': '03', 'name': 'Intensive Care Unit', 'description': 'Critical care and life support'},
        {'id': '04', 'name': 'Cardiology', 'description': 'Heart and cardiovascular care'},
        {'id': '05', 'name': 'Oncology', 'description': 'Cancer treatment and chemotherapy'},
        {'id': '06', 'name': 'Pediatrics', 'description': 'Children and adolescent care'},
        {'id': '07', 'name': 'Surgery', 'description': 'Surgical procedures and recovery'},
        {'id': '08', 'name': 'Neurology', 'description': 'Brain and nervous system disorders'},
        {'id': '09', 'name': 'Orthopedics', 'description': 'Bone and joint treatment'},
        {'id': '10', 'name': 'Psychiatry', 'description': 'Mental health and behavioral care'},
        {'id': '11', 'name': 'Dermatology', 'description': 'Skin and dermatological conditions'}
    ]
    
    for dept in departments:
        dept['created_at'] = (datetime.now() - timedelta(days=random.randint(100, 500))).isoformat()
    
    return departments

def generate_medicines(suppliers):
    """Generate 50 medicine records"""
    medicine_categories = [
        'Analgesics', 'Antibiotics', 'Antivirals', 'Cardiovascular', 'Diabetes',
        'Respiratory', 'Gastrointestinal', 'Neurological', 'Oncology', 'Dermatology'
    ]
    
    medicine_names = [
        'Paracetamol', 'Ibuprofen', 'Aspirin', 'Amoxicillin', 'Azithromycin',
        'Ciprofloxacin', 'Metformin', 'Insulin', 'Lisinopril', 'Amlodipine',
        'Atorvastatin', 'Simvastatin', 'Omeprazole', 'Ranitidine', 'Loratadine',
        'Cetirizine', 'Salbutamol', 'Prednisolone', 'Warfarin', 'Clopidogrel',
        'Morphine', 'Tramadol', 'Diazepam', 'Alprazolam', 'Sertraline',
        'Fluoxetine', 'Levothyroxine', 'Furosemide', 'Hydrochlorothiazide', 'Digoxin',
        'Phenytoin', 'Carbamazepine', 'Gabapentin', 'Pregabalin', 'Metoclopramide',
        'Ondansetron', 'Dexamethasone', 'Hydrocortisone', 'Ketoconazole', 'Fluconazole',
        'Acyclovir', 'Oseltamivir', 'Doxycycline', 'Clarithromycin', 'Vancomycin',
        'Ceftriaxone', 'Meropenem', 'Tazocin', 'Gentamicin', 'Tobramycin'
    ]
    
    medicines = []
    for i, name in enumerate(medicine_names):
        medicine = {
            'id': f"{i+1:02d}",
            'name': name,
            'supplier_id': random.choice(suppliers)['id'],
            'category': random.choice(medicine_categories),
            'form_dosage': random.choice(['Tablet', 'Capsule', 'Injection', 'Syrup', 'Cream', 'Drops']),
            'strength': f"{random.randint(5, 500)}{random.choice(['mg', 'ml', 'g', 'units'])}",
            'low_stock_limit': random.randint(10, 50),
            'unit_price': round(random.uniform(0.5, 100.0), 2),
            'notes': f"Standard {random.choice(medicine_categories).lower()} medication",
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 200))).isoformat()
        }
        medicines.append(medicine)
    
    return medicines

def generate_stores(departments):
    """Generate stores for each department"""
    stores = []
    for dept in departments:
        store = {
            'id': dept['id'],
            'name': f"{dept['name']} Store",
            'department_id': dept['id'],
            'location': f"Building {random.choice(['A', 'B', 'C'])}, Floor {random.randint(1, 5)}",
            'inventory': {},  # Will be populated later
            'created_at': dept['created_at']
        }
        stores.append(store)
    
    return stores

def generate_patients():
    """Generate 15 patient records"""
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa', 'William', 'Jennifer', 'James', 'Mary', 'Christopher', 'Patricia', 'Daniel']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson']
    
    patients = []
    for i in range(15):
        patient = {
            'id': f"{i+1:02d}",
            'name': f"{random.choice(first_names)} {random.choice(last_names)}",
            'age': random.randint(18, 85),
            'gender': random.choice(['Male', 'Female']),
            'phone': f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            'address': f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Cedar'])} Street",
            'medical_history': random.choice(['Diabetes', 'Hypertension', 'Asthma', 'Heart Disease', 'None']),
            'allergies': random.choice(['None', 'Penicillin', 'Aspirin', 'Latex', 'Shellfish']),
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat()
        }
        patients.append(patient)
    
    return patients

def generate_users():
    """Generate additional user accounts"""
    users = [
        {
            'id': '01',
            'username': 'admin',
            'password': '@Xx123456789xX@',
            'role': 'admin',
            'name': 'Waleed Mohamed',
            'email': 'waleed@alorfhospital.com',
            'created_at': datetime.now().isoformat()
        },
        {
            'id': '02',
            'username': 'pharmacy',
            'password': 'pharmacy123',
            'role': 'department_user',
            'name': 'Pharmacy User',
            'email': 'pharmacy@alorfhospital.com',
            'department_id': '01',
            'created_at': datetime.now().isoformat()
        }
    ]
    
    # Add department users
    dept_names = ['emergency', 'icu', 'cardiology', 'oncology', 'pediatrics']
    for i, dept_name in enumerate(dept_names):
        user = {
            'id': f"{i+3:02d}",
            'username': dept_name,
            'password': f"{dept_name}123",
            'role': 'department_user',
            'name': f"{dept_name.title()} User",
            'email': f"{dept_name}@alorfhospital.com",
            'department_id': f"{i+2:02d}",
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
        }
        users.append(user)
    
    return users

def generate_purchases(medicines, suppliers):
    """Generate 10 purchase records"""
    purchases = []

    for i in range(10):
        # Select random supplier
        supplier = random.choice(suppliers)

        # Select 2-5 medicines from this supplier
        supplier_medicines = [m for m in medicines if m['supplier_id'] == supplier['id']]
        selected_medicines = random.sample(supplier_medicines, min(random.randint(2, 5), len(supplier_medicines)))

        purchase_medicines = []
        total_amount = 0

        for medicine in selected_medicines:
            quantity = random.randint(50, 500)
            unit_price = medicine['unit_price']
            total_price = quantity * unit_price
            total_amount += total_price

            purchase_medicines.append({
                'medicine_id': medicine['id'],
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price
            })

        purchase = {
            'id': f"{i+1:02d}",
            'supplier_id': supplier['id'],
            'invoice_number': f"INV-{random.randint(1000, 9999)}",
            'purchase_date': (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()[:10],
            'medicines': purchase_medicines,
            'total_amount': round(total_amount, 2),
            'status': 'completed',
            'notes': f"Bulk purchase from {supplier['name']}",
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()
        }
        purchases.append(purchase)

    return purchases

def update_store_inventories(stores, purchases):
    """Update store inventories based on purchases (add to main store)"""
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

def generate_consumption(patients, medicines, stores):
    """Generate 15 consumption records (1 per patient)"""
    consumption_records = []

    for i, patient in enumerate(patients):
        # Select 1-4 random medicines
        selected_medicines = random.sample(medicines, random.randint(1, 4))

        consumption_medicines = []
        for medicine in selected_medicines:
            quantity = random.randint(1, 10)
            consumption_medicines.append({
                'medicine_id': medicine['id'],
                'quantity': quantity
            })

        consumption = {
            'id': f"{i+1:02d}",
            'patient_id': patient['id'],
            'date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()[:10],
            'medicines': consumption_medicines,
            'prescribed_by': f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Davis'])}",
            'notes': f"Regular medication for {patient['name']}",
            'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        }
        consumption_records.append(consumption)

    return consumption_records

def update_inventories_after_consumption(stores, consumption_records):
    """Update store inventories after consumption (deduct from main store)"""
    main_store = next((s for s in stores if s['id'] == '01'), None)
    if not main_store:
        return

    for consumption in consumption_records:
        for medicine in consumption['medicines']:
            medicine_id = medicine['medicine_id']
            quantity = medicine['quantity']

            if medicine_id in main_store['inventory']:
                main_store['inventory'][medicine_id] = max(0, main_store['inventory'][medicine_id] - quantity)

def generate_transfers(stores, medicines):
    """Generate 10 inventory transfer records"""
    transfers = []
    main_store = next((s for s in stores if s['id'] == '01'), None)
    other_stores = [s for s in stores if s['id'] != '01']

    if not main_store or not other_stores:
        return transfers

    for i in range(10):
        # Select random destination store
        dest_store = random.choice(other_stores)

        # Select 1-3 medicines that have stock in main store
        available_medicines = [m for m in medicines if main_store['inventory'].get(m['id'], 0) > 0]
        if not available_medicines:
            continue

        selected_medicines = random.sample(available_medicines, min(random.randint(1, 3), len(available_medicines)))

        transfer_medicines = []
        for medicine in selected_medicines:
            available_stock = main_store['inventory'].get(medicine['id'], 0)
            if available_stock > 0:
                quantity = random.randint(1, min(available_stock // 2, 20))  # Transfer up to half of stock
                transfer_medicines.append({
                    'medicine_id': medicine['id'],
                    'quantity': quantity
                })

        if transfer_medicines:
            transfer = {
                'id': f"{i+1:02d}",
                'source_store_id': '01',
                'destination_store_id': dest_store['id'],
                'medicines': transfer_medicines,
                'notes': f"Transfer to {dest_store['name']}",
                'status': 'completed',
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 20))).isoformat()
            }
            transfers.append(transfer)

    return transfers

def update_inventories_after_transfers(stores, transfers):
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

def save_sample_data():
    """Save generated sample data to JSON files"""
    print("Generating comprehensive sample data...")

    # Generate all sample data
    sample_data = generate_sample_data()

    # Save each data type to its respective file
    for data_type, data in sample_data.items():
        if data_type in DB_FILES:
            file_path = DB_FILES[data_type]

            # Create backup of existing data
            if os.path.exists(file_path):
                backup_path = file_path.replace('.json', '_backup.json')
                os.rename(file_path, backup_path)
                print(f"Backed up existing {data_type}.json to {data_type}_backup.json")

            # Save new data
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Generated {len(data)} {data_type} records")

    print("\nSample data generation completed!")
    print("Summary:")
    print(f"- {len(sample_data['suppliers'])} suppliers")
    print(f"- {len(sample_data['departments'])} departments")
    print(f"- {len(sample_data['medicines'])} medicines")
    print(f"- {len(sample_data['stores'])} stores")
    print(f"- {len(sample_data['patients'])} patients")
    print(f"- {len(sample_data['purchases'])} purchases")
    print(f"- {len(sample_data['consumption'])} consumption records")
    print(f"- {len(sample_data['transfers'])} transfers")
    print(f"- {len(sample_data['users'])} users")

if __name__ == "__main__":
    save_sample_data()
