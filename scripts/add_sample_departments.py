#!/usr/bin/env python3
"""
Script to add 5 new departments with corresponding stores
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_departments, get_stores, get_medicines, save_data, load_data, generate_id
from datetime import datetime
import random

def generate_new_departments():
    """Generate 5 new departments with stores"""
    
    # Get existing data
    departments = load_data('departments')
    stores = load_data('stores')
    medicines = get_medicines()
    medicine_ids = [m['id'] for m in medicines]
    
    # New department data
    new_departments_data = [
        {
            "name": "Orthopedics",
            "responsible_person": "Dr. Michael Rodriguez",
            "telephone": "+1-555-0111",
            "notes": "Bone, joint, and musculoskeletal care - orthopedic medications and rehabilitation"
        },
        {
            "name": "Dermatology", 
            "responsible_person": "Dr. Sarah Williams",
            "telephone": "+1-555-0112",
            "notes": "Skin, hair, and nail disorders - dermatological treatments and medications"
        },
        {
            "name": "Ophthalmology",
            "responsible_person": "Dr. Kevin Thompson",
            "telephone": "+1-555-0113", 
            "notes": "Eye and vision care - ophthalmological medications and treatments"
        },
        {
            "name": "Endocrinology",
            "responsible_person": "Dr. Rachel Martinez",
            "telephone": "+1-555-0114",
            "notes": "Hormone and metabolic disorders - endocrine medications and diabetes management"
        },
        {
            "name": "Gastroenterology",
            "responsible_person": "Dr. Daniel Garcia",
            "telephone": "+1-555-0115",
            "notes": "Digestive system disorders - gastrointestinal medications and treatments"
        }
    ]
    
    print(f"Adding 5 new departments with corresponding stores...")
    
    # Get current max IDs to avoid conflicts
    dept_ids = [int(d['id']) for d in departments if d['id'].isdigit()]
    store_ids = [int(s['id']) for s in stores if s['id'].isdigit()]
    next_dept_id = max(dept_ids) + 1 if dept_ids else 1
    next_store_id = max(store_ids) + 1 if store_ids else 1

    for i, dept_data in enumerate(new_departments_data, 1):
        # Generate unique department ID
        dept_id = f"{next_dept_id:02d}"
        next_dept_id += 1

        # Create department record
        department_record = {
            'id': dept_id,
            'name': dept_data['name'],
            'responsible_person': dept_data['responsible_person'],
            'telephone': dept_data['telephone'],
            'notes': dept_data['notes'],
            'created_at': datetime.now().isoformat()
        }

        # Add department
        departments.append(department_record)

        # Generate unique store ID
        store_id = f"{next_store_id:02d}"
        next_store_id += 1

        # Generate realistic inventory for the store (20-30 medicines with random quantities)
        num_medicines = random.randint(20, 30)
        selected_medicines = random.sample(medicine_ids, min(num_medicines, len(medicine_ids)))

        inventory = {}
        for med_id in selected_medicines:
            quantity = random.randint(50, 500)
            inventory[med_id] = quantity

        store_record = {
            'id': store_id,
            'name': f"{dept_data['name']} Store",
            'department_id': dept_id,
            'inventory': inventory,
            'created_at': datetime.now().isoformat(),
            'notes': f"Specialized store for {dept_data['name']} department"
        }

        # Add store
        stores.append(store_record)

        print(f"✓ Added department {i}/5: {dept_data['name']} (ID: {dept_id}) with store (ID: {store_id})")
    
    # Save both departments and stores
    save_data('departments', departments)
    save_data('stores', stores)
    
    print(f"\n✅ Successfully added 5 new departments with corresponding stores!")
    print(f"📊 Total departments: {len(departments)}")
    print(f"📦 Total stores: {len(stores)}")

if __name__ == "__main__":
    generate_new_departments()
