#!/usr/bin/env python3
"""
Script to add 50 new sample patient records with realistic data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import save_patient, get_departments
from datetime import datetime, timedelta
import random

def generate_realistic_patients():
    """Generate 50 realistic patient records"""
    
    # Get available departments
    departments = get_departments()
    department_ids = [d['id'] for d in departments]
    
    # Realistic patient names
    first_names_male = [
        "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", 
        "Thomas", "Christopher", "Charles", "Daniel", "Matthew", "Anthony", "Mark", 
        "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian",
        "George", "Timothy", "Ronald", "Jason", "Edward", "Jeffrey", "Ryan", "Jacob"
    ]
    
    first_names_female = [
        "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", 
        "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty", "Helen", "Sandra",
        "Donna", "Carol", "Ruth", "Sharon", "Michelle", "Laura", "Sarah", "Kimberly",
        "Deborah", "Dorothy", "Lisa", "Nancy", "Karen", "Betty", "Helen", "Sandra"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
        "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
    ]
    
    # Medical conditions
    medical_conditions = [
        "Hypertension", "Diabetes Type 2", "Asthma", "Arthritis", "Depression",
        "Anxiety", "COPD", "Heart Disease", "Osteoporosis", "Migraine",
        "Allergic Rhinitis", "Gastroesophageal Reflux", "Hypothyroidism", 
        "Chronic Pain", "Insomnia", "High Cholesterol", "Kidney Disease",
        "Liver Disease", "Anemia", "Chronic Fatigue", "Fibromyalgia"
    ]
    
    # Common allergies
    allergies = [
        "Penicillin", "Sulfa drugs", "Aspirin", "Ibuprofen", "Shellfish",
        "Nuts", "Latex", "Codeine", "Morphine", "Contrast dye", "None known",
        "Pollen", "Dust mites", "Pet dander", "Eggs", "Milk", "Soy"
    ]
    
    # Street names for addresses
    street_names = [
        "Main Street", "Oak Avenue", "Pine Road", "Cedar Lane", "Maple Drive",
        "Elm Street", "Park Avenue", "First Street", "Second Avenue", "Third Street",
        "Washington Street", "Lincoln Avenue", "Jefferson Road", "Madison Lane",
        "Franklin Street", "Church Street", "School Road", "Mill Street", "Hill Avenue"
    ]
    
    print(f"Adding 50 new patient records...")
    
    for i in range(1, 51):
        # Generate random patient data
        gender = random.choice(["Male", "Female"])
        if gender == "Male":
            first_name = random.choice(first_names_male)
        else:
            first_name = random.choice(first_names_female)
        
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        # Generate realistic data
        patient_record = {
            'name': full_name,
            'age': random.randint(18, 85),
            'gender': gender,
            'phone': generate_phone_number(),
            'address': f"{random.randint(100, 9999)} {random.choice(street_names)}",
            'medical_history': random.choice(medical_conditions),
            'allergies': random.choice(allergies),
            'department_id': random.choice(department_ids),
            'file_no': generate_file_number(),
            'date_of_entry': generate_entry_date(),
            'notes': generate_patient_notes()
        }
        
        try:
            patient_id = save_patient(patient_record)
            print(f"✓ Added patient {i}/50: {full_name} (ID: {patient_id})")
        except Exception as e:
            print(f"✗ Error adding patient {full_name}: {e}")
    
    print(f"\n✅ Successfully added 50 new patient records!")

def generate_phone_number():
    """Generate realistic phone number"""
    area_code = random.randint(200, 999)
    exchange = random.randint(200, 999)
    number = random.randint(1000, 9999)
    return f"+1-555-{exchange:03d}-{number:04d}"

def generate_file_number():
    """Generate realistic medical file number"""
    prefix = random.choice(['P', 'M', 'F', 'R', 'H'])
    number = random.randint(1000, 9999)
    return f"{prefix}{number}"

def generate_entry_date():
    """Generate realistic entry date (within last 2 years)"""
    days_ago = random.randint(1, 730)  # 1 day to 2 years ago
    entry_date = datetime.now() - timedelta(days=days_ago)
    return entry_date.strftime('%Y-%m-%d')

def generate_patient_notes():
    """Generate realistic patient notes"""
    notes_options = [
        "Regular follow-up required",
        "Stable condition, monitoring ongoing",
        "Medication compliance good",
        "Requires dietary counseling",
        "Physical therapy recommended",
        "Chronic condition management",
        "Routine monitoring needed",
        "Patient education provided",
        "Family history significant",
        "Lifestyle modifications advised",
        "Regular lab work required",
        "Specialist referral made",
        "Treatment plan updated",
        "Patient cooperative with treatment",
        "Medication adjustment needed",
        "Good response to current therapy",
        "Requires close monitoring",
        "Patient counseled on side effects",
        "Follow-up in 3 months",
        "Condition improving steadily"
    ]
    return random.choice(notes_options)

if __name__ == "__main__":
    generate_realistic_patients()
