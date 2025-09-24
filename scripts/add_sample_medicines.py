#!/usr/bin/env python3
"""
Script to add 50 new sample medicine records with realistic data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import save_medicine, get_suppliers
from datetime import datetime, timedelta
import random

def generate_realistic_medicines():
    """Generate 50 realistic medicine records"""
    
    # Get available suppliers
    suppliers = get_suppliers()
    supplier_ids = [s['id'] for s in suppliers]
    
    # Realistic medicine data
    medicines_data = [
        # Cardiovascular medicines
        {"name": "Atorvastatin", "category": "Cardiovascular", "form_dosage": "Tablet 20mg", "notes": "Cholesterol-lowering medication"},
        {"name": "Metoprolol", "category": "Cardiovascular", "form_dosage": "Tablet 50mg", "notes": "Beta-blocker for hypertension"},
        {"name": "Lisinopril", "category": "Cardiovascular", "form_dosage": "Tablet 10mg", "notes": "ACE inhibitor for blood pressure"},
        {"name": "Clopidogrel", "category": "Cardiovascular", "form_dosage": "Tablet 75mg", "notes": "Antiplatelet medication"},
        {"name": "Warfarin", "category": "Cardiovascular", "form_dosage": "Tablet 5mg", "notes": "Anticoagulant medication"},
        
        # Antibiotics
        {"name": "Azithromycin", "category": "Antibiotic", "form_dosage": "Tablet 500mg", "notes": "Broad-spectrum antibiotic"},
        {"name": "Ciprofloxacin", "category": "Antibiotic", "form_dosage": "Tablet 500mg", "notes": "Fluoroquinolone antibiotic"},
        {"name": "Doxycycline", "category": "Antibiotic", "form_dosage": "Capsule 100mg", "notes": "Tetracycline antibiotic"},
        {"name": "Clindamycin", "category": "Antibiotic", "form_dosage": "Capsule 300mg", "notes": "Lincosamide antibiotic"},
        {"name": "Cephalexin", "category": "Antibiotic", "form_dosage": "Capsule 500mg", "notes": "Cephalosporin antibiotic"},
        
        # Pain management
        {"name": "Tramadol", "category": "Analgesic", "form_dosage": "Tablet 50mg", "notes": "Opioid pain medication"},
        {"name": "Naproxen", "category": "Analgesic", "form_dosage": "Tablet 500mg", "notes": "NSAID for pain and inflammation"},
        {"name": "Diclofenac", "category": "Analgesic", "form_dosage": "Gel 1%", "notes": "Topical anti-inflammatory"},
        {"name": "Codeine", "category": "Analgesic", "form_dosage": "Tablet 30mg", "notes": "Opioid analgesic"},
        {"name": "Morphine", "category": "Analgesic", "form_dosage": "Injection 10mg/ml", "notes": "Strong opioid analgesic"},
        
        # Diabetes medications
        {"name": "Metformin", "category": "Antidiabetic", "form_dosage": "Tablet 500mg", "notes": "First-line diabetes medication"},
        {"name": "Insulin Glargine", "category": "Antidiabetic", "form_dosage": "Injection 100 units/ml", "notes": "Long-acting insulin"},
        {"name": "Gliclazide", "category": "Antidiabetic", "form_dosage": "Tablet 80mg", "notes": "Sulfonylurea for diabetes"},
        {"name": "Sitagliptin", "category": "Antidiabetic", "form_dosage": "Tablet 100mg", "notes": "DPP-4 inhibitor"},
        {"name": "Insulin Aspart", "category": "Antidiabetic", "form_dosage": "Injection 100 units/ml", "notes": "Rapid-acting insulin"},
        
        # Respiratory medications
        {"name": "Salbutamol", "category": "Respiratory", "form_dosage": "Inhaler 100mcg", "notes": "Bronchodilator for asthma"},
        {"name": "Budesonide", "category": "Respiratory", "form_dosage": "Inhaler 200mcg", "notes": "Corticosteroid inhaler"},
        {"name": "Montelukast", "category": "Respiratory", "form_dosage": "Tablet 10mg", "notes": "Leukotriene receptor antagonist"},
        {"name": "Theophylline", "category": "Respiratory", "form_dosage": "Tablet 200mg", "notes": "Bronchodilator medication"},
        {"name": "Ipratropium", "category": "Respiratory", "form_dosage": "Inhaler 20mcg", "notes": "Anticholinergic bronchodilator"},
        
        # Gastrointestinal medications
        {"name": "Omeprazole", "category": "Gastrointestinal", "form_dosage": "Capsule 20mg", "notes": "Proton pump inhibitor"},
        {"name": "Ranitidine", "category": "Gastrointestinal", "form_dosage": "Tablet 150mg", "notes": "H2 receptor antagonist"},
        {"name": "Loperamide", "category": "Gastrointestinal", "form_dosage": "Capsule 2mg", "notes": "Anti-diarrheal medication"},
        {"name": "Simethicone", "category": "Gastrointestinal", "form_dosage": "Tablet 40mg", "notes": "Anti-flatulent medication"},
        {"name": "Domperidone", "category": "Gastrointestinal", "form_dosage": "Tablet 10mg", "notes": "Prokinetic agent"},
        
        # Neurological medications
        {"name": "Gabapentin", "category": "Neurological", "form_dosage": "Capsule 300mg", "notes": "Anticonvulsant for neuropathic pain"},
        {"name": "Levetiracetam", "category": "Neurological", "form_dosage": "Tablet 500mg", "notes": "Antiepileptic medication"},
        {"name": "Carbamazepine", "category": "Neurological", "form_dosage": "Tablet 200mg", "notes": "Anticonvulsant medication"},
        {"name": "Phenytoin", "category": "Neurological", "form_dosage": "Capsule 100mg", "notes": "Antiepileptic drug"},
        {"name": "Valproic Acid", "category": "Neurological", "form_dosage": "Tablet 500mg", "notes": "Mood stabilizer and anticonvulsant"},
        
        # Psychiatric medications
        {"name": "Sertraline", "category": "Psychiatric", "form_dosage": "Tablet 50mg", "notes": "SSRI antidepressant"},
        {"name": "Fluoxetine", "category": "Psychiatric", "form_dosage": "Capsule 20mg", "notes": "SSRI antidepressant"},
        {"name": "Lorazepam", "category": "Psychiatric", "form_dosage": "Tablet 1mg", "notes": "Benzodiazepine for anxiety"},
        {"name": "Risperidone", "category": "Psychiatric", "form_dosage": "Tablet 2mg", "notes": "Atypical antipsychotic"},
        {"name": "Lithium", "category": "Psychiatric", "form_dosage": "Tablet 300mg", "notes": "Mood stabilizer"},
        
        # Dermatological medications
        {"name": "Hydrocortisone", "category": "Dermatological", "form_dosage": "Cream 1%", "notes": "Topical corticosteroid"},
        {"name": "Clotrimazole", "category": "Dermatological", "form_dosage": "Cream 1%", "notes": "Antifungal cream"},
        {"name": "Mupirocin", "category": "Dermatological", "form_dosage": "Ointment 2%", "notes": "Topical antibiotic"},
        {"name": "Tretinoin", "category": "Dermatological", "form_dosage": "Gel 0.025%", "notes": "Topical retinoid"},
        {"name": "Calamine", "category": "Dermatological", "form_dosage": "Lotion", "notes": "Soothing skin lotion"},
        
        # Ophthalmological medications
        {"name": "Timolol", "category": "Ophthalmological", "form_dosage": "Eye Drops 0.5%", "notes": "Beta-blocker for glaucoma"},
        {"name": "Chloramphenicol", "category": "Ophthalmological", "form_dosage": "Eye Drops 0.5%", "notes": "Antibiotic eye drops"},
        {"name": "Prednisolone", "category": "Ophthalmological", "form_dosage": "Eye Drops 1%", "notes": "Corticosteroid eye drops"},
        {"name": "Artificial Tears", "category": "Ophthalmological", "form_dosage": "Eye Drops", "notes": "Lubricating eye drops"},
        {"name": "Cyclopentolate", "category": "Ophthalmological", "form_dosage": "Eye Drops 1%", "notes": "Mydriatic eye drops"},
        
        # Vitamins and supplements
        {"name": "Vitamin D3", "category": "Vitamin", "form_dosage": "Tablet 1000 IU", "notes": "Cholecalciferol supplement"},
        {"name": "Folic Acid", "category": "Vitamin", "form_dosage": "Tablet 5mg", "notes": "Vitamin B9 supplement"}
    ]
    
    print(f"Adding {len(medicines_data)} new medicine records...")
    
    for i, med_data in enumerate(medicines_data, 1):
        # Generate realistic data for each medicine
        medicine_record = {
            'name': med_data['name'],
            'supplier_id': random.choice(supplier_ids),
            'form_dosage': med_data['form_dosage'],
            'low_stock_limit': random.randint(15, 50),
            'notes': med_data['notes'],
            'expiry_date': generate_expiry_date(),
            'batch_number': generate_batch_number(),
            'barcode_number': generate_barcode()
        }
        
        try:
            medicine_id = save_medicine(medicine_record)
            print(f"✓ Added medicine {i}/50: {med_data['name']} (ID: {medicine_id})")
        except Exception as e:
            print(f"✗ Error adding medicine {med_data['name']}: {e}")
    
    print(f"\n✅ Successfully added {len(medicines_data)} new medicine records!")

def generate_expiry_date():
    """Generate realistic expiry date (6 months to 3 years from now)"""
    days_ahead = random.randint(180, 1095)  # 6 months to 3 years
    expiry_date = datetime.now() + timedelta(days=days_ahead)
    return expiry_date.strftime('%Y-%m-%d')

def generate_batch_number():
    """Generate realistic batch number"""
    prefix = random.choice(['LOT', 'BAT', 'BTH', 'LT'])
    number = random.randint(100000, 999999)
    return f"{prefix}{number}"

def generate_barcode():
    """Generate realistic barcode number (13 digits)"""
    return ''.join([str(random.randint(0, 9)) for _ in range(13)])

if __name__ == "__main__":
    generate_realistic_medicines()
