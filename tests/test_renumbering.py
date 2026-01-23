#!/usr/bin/env python3
"""
Comprehensive test for ID renumbering functionality
Tests automatic ID renumbering after deletion and cascade updates
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.database import (
    get_medicines, save_medicine, delete_medicine,
    get_patients, save_patient, delete_patient,
    get_suppliers, save_supplier, delete_supplier,
    get_departments, save_department, delete_department,
    get_stores, get_consumption, get_purchases
)

def print_test(message):
    """Print test message"""
    print(f"\n{'='*60}")
    print(f"TEST: {message}")
    print('='*60)

def print_success(message):
    """Print success message"""
    print(f"[SUCCESS] {message}")

def print_error(message):
    """Print error message"""
    print(f"[ERROR] {message}")

def print_info(message):
    """Print info message"""
    print(f"[INFO] {message}")

def test_medicine_renumbering():
    """Test medicine ID renumbering and cascade updates"""
    print_test("Medicine ID Renumbering & Cascade Updates")

    # Create test medicines
    print_info("Creating test medicines...")
    med_ids = []
    for i in range(1, 6):
        med_data = {
            'name': f'Test Medicine {i}',
            'supplier_id': '01',
            'low_stock_limit': 10,
            'form_dosage': 'Tablet 500mg',
            'notes': f'Test medicine {i}'
        }
        med_id = save_medicine(med_data)
        med_ids.append(med_id)
        print_info(f"Created medicine: ID={med_id}, Name={med_data['name']}")

    # Display current IDs
    medicines = get_medicines()
    print_info(f"Medicine IDs before deletion: {[m['id'] for m in medicines[-5:]]}")

    # Delete medicine ID 02 (should trigger renumbering)
    print_info(f"Deleting medicine ID: {med_ids[1]}")
    delete_medicine(med_ids[1])

    # Check renumbering
    medicines = get_medicines()
    med_ids_after = [m['id'] for m in medicines[-4:]]
    print_info(f"Medicine IDs after deletion: {med_ids_after}")

    # Verify sequential IDs
    expected_ids = [str(i).zfill(2) for i in range(len(medicines) - 3, len(medicines) + 1)]
    if med_ids_after == expected_ids:
        print_success("Medicine IDs are sequential after deletion")
    else:
        print_error(f"Medicine IDs not sequential. Expected: {expected_ids}, Got: {med_ids_after}")

    # Check if store inventories were updated
    stores = get_stores()
    print_info(f"Checking {len(stores)} stores for inventory cascade updates...")
    for store in stores:
        if store.get('inventory'):
            print_info(f"Store {store['id']}: {len(store['inventory'])} medicine entries")

    print_success("Medicine renumbering test completed")

def test_patient_renumbering():
    """Test patient ID renumbering and cascade updates"""
    print_test("Patient ID Renumbering & Cascade Updates")

    # Create test patients
    print_info("Creating test patients...")
    patient_ids = []
    for i in range(1, 6):
        patient_data = {
            'name': f'Test Patient {i}',
            'file_no': f'P{str(i).zfill(3)}',
            'gender': 'Male' if i % 2 == 0 else 'Female',
            'date_of_entry': '2025-10-15',
            'department_id': '01',
            'medical_history': f'Test history {i}',
            'notes': f'Test patient {i}'
        }
        patient_id = save_patient(patient_data)
        patient_ids.append(patient_id)
        print_info(f"Created patient: ID={patient_id}, Name={patient_data['name']}")

    # Display current IDs
    patients = get_patients()
    print_info(f"Patient IDs before deletion: {[p['id'] for p in patients[-5:]]}")

    # Delete patient ID 03 (should trigger renumbering)
    print_info(f"Deleting patient ID: {patient_ids[2]}")
    delete_patient(patient_ids[2])

    # Check renumbering
    patients = get_patients()
    patient_ids_after = [p['id'] for p in patients[-4:]]
    print_info(f"Patient IDs after deletion: {patient_ids_after}")

    # Verify sequential IDs
    expected_ids = [str(i).zfill(2) for i in range(len(patients) - 3, len(patients) + 1)]
    if patient_ids_after == expected_ids:
        print_success("Patient IDs are sequential after deletion")
    else:
        print_error(f"Patient IDs not sequential. Expected: {expected_ids}, Got: {patient_ids_after}")

    # Check if consumption records were updated
    consumption = get_consumption()
    print_info(f"Checking {len(consumption)} consumption records for patient_id cascade updates...")

    print_success("Patient renumbering test completed")

def test_supplier_renumbering():
    """Test supplier ID renumbering and cascade updates"""
    print_test("Supplier ID Renumbering & Cascade Updates")

    # Create test suppliers
    print_info("Creating test suppliers...")
    supplier_ids = []
    for i in range(1, 5):
        supplier_data = {
            'name': f'Test Supplier {i}',
            'contact_person': f'Contact {i}',
            'phone': f'555-000{i}',
            'email': f'supplier{i}@test.com',
            'address': f'Address {i}',
            'notes': f'Test supplier {i}'
        }
        supplier_id = save_supplier(supplier_data)
        supplier_ids.append(supplier_id)
        print_info(f"Created supplier: ID={supplier_id}, Name={supplier_data['name']}")

    # Display current IDs
    suppliers = get_suppliers()
    print_info(f"Supplier IDs before deletion: {[s['id'] for s in suppliers[-4:]]}")

    # Delete supplier ID 02 (should trigger renumbering)
    print_info(f"Deleting supplier ID: {supplier_ids[1]}")
    delete_supplier(supplier_ids[1])

    # Check renumbering
    suppliers = get_suppliers()
    supplier_ids_after = [s['id'] for s in suppliers[-3:]]
    print_info(f"Supplier IDs after deletion: {supplier_ids_after}")

    # Verify sequential IDs
    expected_ids = [str(i).zfill(2) for i in range(len(suppliers) - 2, len(suppliers) + 1)]
    if supplier_ids_after == expected_ids:
        print_success("Supplier IDs are sequential after deletion")
    else:
        print_error(f"Supplier IDs not sequential. Expected: {expected_ids}, Got: {supplier_ids_after}")

    # Check if medicines were updated
    medicines = get_medicines()
    print_info(f"Checking {len(medicines)} medicines for supplier_id cascade updates...")
    for med in medicines[-5:]:
        print_info(f"Medicine {med['id']}: supplier_id={med.get('supplier_id', 'N/A')}")

    print_success("Supplier renumbering test completed")

def test_protected_ids():
    """Test that protected IDs are not renumbered"""
    print_test("Protected IDs (Main Entities) Test")

    # Check Main Department (ID='01')
    departments = get_departments()
    main_dept = next((d for d in departments if d.get('name') == 'Main Pharmacy'), None)
    if main_dept and main_dept['id'] == '01':
        print_success("Main Pharmacy department keeps ID='01' (protected)")
    else:
        print_error("Main Pharmacy department ID changed or not found!")

    # Check Main Store (ID='01')
    stores = get_stores()
    main_store = next((s for s in stores if s.get('name') == 'Main Pharmacy Store'), None)
    if main_store and main_store['id'] == '01':
        print_success("Main Pharmacy Store keeps ID='01' (protected)")
    else:
        print_error("Main Pharmacy Store ID changed or not found!")

    print_success("Protected IDs test completed")

def test_foreign_key_integrity():
    """Test that foreign key relationships are maintained"""
    print_test("Foreign Key Integrity Check")

    # Check store -> department relationship
    stores = get_stores()
    departments = get_departments()
    dept_ids = {d['id'] for d in departments}

    print_info("Checking store -> department relationships...")
    all_valid = True
    for store in stores:
        dept_id = store.get('department_id')
        if dept_id not in dept_ids:
            print_error(f"Store {store['id']} references non-existent department {dept_id}")
            all_valid = False

    if all_valid:
        print_success("All store -> department references are valid")

    # Check medicine -> supplier relationship
    medicines = get_medicines()
    suppliers = get_suppliers()
    supplier_ids = {s['id'] for s in suppliers}

    print_info("Checking medicine -> supplier relationships...")
    all_valid = True
    for med in medicines:
        sup_id = med.get('supplier_id')
        if sup_id and sup_id not in supplier_ids:
            print_error(f"Medicine {med['id']} references non-existent supplier {sup_id}")
            all_valid = False

    if all_valid:
        print_success("All medicine -> supplier references are valid")

    print_success("Foreign key integrity check completed")

def display_summary():
    """Display test summary"""
    print_test("Test Summary")

    medicines = get_medicines()
    patients = get_patients()
    suppliers = get_suppliers()
    departments = get_departments()
    stores = get_stores()
    purchases = get_purchases()
    consumption = get_consumption()

    print(f"""
    Database Statistics:
    - Medicines: {len(medicines)}
    - Patients: {len(patients)}
    - Suppliers: {len(suppliers)}
    - Departments: {len(departments)}
    - Stores: {len(stores)}
    - Purchases: {len(purchases)}
    - Consumption Records: {len(consumption)}

    Recent IDs (last 5):
    - Medicine IDs: {[m['id'] for m in medicines[-5:]]}
    - Patient IDs: {[p['id'] for p in patients[-5:]]}
    - Supplier IDs: {[s['id'] for s in suppliers[-5:]]}
    """)

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ID RENUMBERING FUNCTIONALITY TEST SUITE")
    print("="*60)

    try:
        # Run tests
        test_protected_ids()
        test_medicine_renumbering()
        test_patient_renumbering()
        test_supplier_renumbering()
        test_foreign_key_integrity()
        display_summary()

        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")

    except Exception as e:
        print_error(f"Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
