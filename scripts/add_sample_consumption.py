#!/usr/bin/env python3
"""
Script to add 300 new sample consumption records with realistic data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_patients, get_medicines, get_departments, save_data, load_data, generate_id
from datetime import datetime, timedelta
import random

def generate_realistic_consumption():
    """Generate 300 realistic consumption records"""
    
    # Get available data
    patients = get_patients()
    medicines = get_medicines()
    departments = get_departments()
    
    patient_ids = [p['id'] for p in patients]
    medicine_ids = [m['id'] for m in medicines]
    department_ids = [d['id'] for d in departments]
    
    # Doctor names for prescriptions
    doctors = [
        "Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. David Wilson", "Dr. Lisa Thompson",
        "Dr. James Anderson", "Dr. Robert Martinez", "Dr. Emily Davis", "Dr. Christopher Lee",
        "Dr. Maria Rodriguez", "Dr. Kevin Brown", "Dr. Jennifer Taylor", "Dr. Mark Wilson",
        "Dr. Amanda Garcia", "Dr. Daniel Miller", "Dr. Rachel Thompson", "Dr. Steven Clark"
    ]
    
    print(f"Adding 300 new consumption records...")
    
    consumption_records = load_data('consumption')
    
    for i in range(1, 301):
        # Select random patient and get their department
        patient_id = random.choice(patient_ids)
        patient = next(p for p in patients if p['id'] == patient_id)
        patient_department = patient.get('department_id', random.choice(department_ids))
        
        # Generate medicines for this consumption (1-3 medicines per record)
        num_medicines = random.randint(1, 3)
        selected_medicines = random.sample(medicine_ids, min(num_medicines, len(medicine_ids)))
        
        medicines_list = []
        for med_id in selected_medicines:
            quantity = random.randint(1, 10)  # Realistic consumption quantities
            medicines_list.append({
                "medicine_id": med_id,
                "quantity": quantity
            })
        
        # Generate consumption record
        consumption_record = {
            'id': generate_id('consumption'),
            'patient_id': patient_id,
            'date': generate_consumption_date(),
            'medicines': medicines_list,
            'prescribed_by': random.choice(doctors),
            'notes': generate_consumption_notes(patient['name']),
            'created_at': datetime.now().isoformat(),
            'department_id': patient_department
        }
        
        try:
            consumption_records.append(consumption_record)
            if i % 50 == 0:  # Progress update every 50 records
                print(f"✓ Added {i}/300 consumption records...")
        except Exception as e:
            print(f"✗ Error adding consumption record {i}: {e}")
    
    # Save all consumption records
    save_data('consumption', consumption_records)
    print(f"\n✅ Successfully added 300 new consumption records!")

def generate_consumption_date():
    """Generate realistic consumption date (within last 3 months)"""
    days_ago = random.randint(1, 90)  # 1 day to 3 months ago
    consumption_date = datetime.now() - timedelta(days=days_ago)
    return consumption_date.strftime('%Y-%m-%d')

def generate_consumption_notes(patient_name):
    """Generate realistic consumption notes"""
    notes_templates = [
        f"Regular medication for {patient_name}",
        f"Prescribed medication dispensed to {patient_name}",
        f"Follow-up medication for {patient_name}",
        f"Chronic condition management for {patient_name}",
        f"Pain management medication for {patient_name}",
        f"Preventive medication for {patient_name}",
        f"Emergency medication dispensed to {patient_name}",
        f"Post-operative medication for {patient_name}",
        f"Maintenance therapy for {patient_name}",
        f"Acute treatment medication for {patient_name}",
        f"Routine prescription refill for {patient_name}",
        f"Specialist-recommended medication for {patient_name}",
        f"Symptom management medication for {patient_name}",
        f"Therapeutic medication for {patient_name}",
        f"Recovery medication for {patient_name}"
    ]
    return random.choice(notes_templates)

if __name__ == "__main__":
    generate_realistic_consumption()
