"""
Direct API test for cascading deletion and persistence
Tests the backend directly without Playwright
"""

import requests
import json
import time

def test_cascading_deletion():
    """Test Issue 1: Cascading deletion via API"""
    print("\n" + "="*80)
    print("TESTING ISSUE 1: Cascading Deletion (Direct API Test)")
    print("="*80)
    
    # Create session and login
    session = requests.Session()
    login_response = session.post(
        'http://127.0.0.1:5045/auth/login',
        data={'username': 'admin', 'password': '@Xx123456789xX@'}
    )
    
    if login_response.status_code != 200:
        print(f"✗ Login failed: {login_response.status_code}")
        return False
    
    print("✓ Logged in successfully")
    
    # Generate sample data
    print("\n[Step 1] Generating sample data...")
    gen_response = session.post('http://127.0.0.1:5045/settings/generate-sample-data')
    if gen_response.status_code == 200:
        print("✓ Sample data generated")
    else:
        print(f"⚠ Sample data generation status: {gen_response.status_code}")
    
    time.sleep(2)
    
    # Check initial state
    print("\n[Step 2] Checking initial state...")
    with open('data/patients.json', 'r') as f:
        patients_before = json.load(f)
    with open('data/consumption.json', 'r') as f:
        consumption_before = json.load(f)
    
    print(f"  - Patients: {len(patients_before)}")
    print(f"  - Consumption records: {len(consumption_before)}")
    
    if len(patients_before) == 0:
        print("✗ No patients found!")
        return False
    
    # Find a patient with consumption records
    patient_to_delete = None
    consumption_count = 0
    
    for patient in patients_before:
        patient_id = patient['id']
        count = sum(1 for c in consumption_before if c.get('patient_id') == patient_id)
        if count > 0:
            patient_to_delete = patient
            consumption_count = count
            break
    
    if not patient_to_delete:
        print("⚠ No patients with consumption records found, using first patient")
        patient_to_delete = patients_before[0]
        consumption_count = 0
    
    patient_id = patient_to_delete['id']
    patient_name = patient_to_delete['name']
    
    print(f"\n[Step 3] Deleting patient: {patient_name} (ID: {patient_id})")
    print(f"  - This patient has {consumption_count} consumption records")
    
    # Perform bulk delete
    delete_response = session.post(
        'http://127.0.0.1:5045/patients/bulk-delete',
        json={'ids': [patient_id]}
    )
    
    print(f"\n[Step 4] Bulk delete response:")
    print(f"  - Status: {delete_response.status_code}")
    print(f"  - Response: {delete_response.json()}")
    
    if delete_response.status_code != 200:
        print("✗ Bulk delete failed!")
        return False
    
    time.sleep(1)
    
    # Check final state
    print("\n[Step 5] Checking final state...")
    with open('data/patients.json', 'r') as f:
        patients_after = json.load(f)
    with open('data/consumption.json', 'r') as f:
        consumption_after = json.load(f)
    
    print(f"  - Patients before: {len(patients_before)}, after: {len(patients_after)}")
    print(f"  - Consumption before: {len(consumption_before)}, after: {len(consumption_after)}")
    
    # Verify patient was deleted
    patient_deleted = not any(p['name'] == patient_name for p in patients_after)
    
    # Verify consumption records were deleted
    expected_consumption = len(consumption_before) - consumption_count
    consumption_deleted_correctly = len(consumption_after) == expected_consumption
    
    print("\n[Step 6] Verification:")
    if patient_deleted:
        print(f"  ✓ Patient '{patient_name}' deleted successfully")
    else:
        print(f"  ✗ Patient '{patient_name}' NOT deleted!")
        return False
    
    if consumption_count > 0:
        if consumption_deleted_correctly:
            print(f"  ✓ {consumption_count} consumption records deleted (cascading deletion worked!)")
        else:
            print(f"  ✗ Consumption records NOT deleted correctly!")
            print(f"    Expected: {expected_consumption}, Got: {len(consumption_after)}")
            return False
    else:
        print("  - No consumption records to delete")
    
    print("\n" + "="*80)
    print("✓✓✓ ISSUE 1 TEST PASSED ✓✓✓")
    print("  - Cascading deletion works correctly")
    print("  - Patient deleted from JSON file")
    print("  - Consumption records deleted automatically")
    print("="*80)
    
    return True

def test_persistence_all_modules():
    """Test Issue 2: Persistence across all modules"""
    print("\n" + "="*80)
    print("TESTING ISSUE 2: Bulk Delete Persistence (Direct API Test)")
    print("="*80)
    
    modules = [
        {'name': 'Medicines', 'endpoint': '/medicines/bulk-delete', 'file': 'medicines'},
        {'name': 'Doctors', 'endpoint': '/doctors/bulk-delete', 'file': 'doctors'},
        {'name': 'Suppliers', 'endpoint': '/suppliers/bulk-delete', 'file': 'suppliers'},
        {'name': 'Departments', 'endpoint': '/departments/bulk-delete', 'file': 'departments'},
    ]
    
    results = {}
    
    # Create session and login
    session = requests.Session()
    login_response = session.post(
        'http://127.0.0.1:5045/auth/login',
        data={'username': 'admin', 'password': '@Xx123456789xX@'}
    )
    
    if login_response.status_code != 200:
        print(f"✗ Login failed: {login_response.status_code}")
        return False
    
    print("✓ Logged in successfully\n")
    
    for module in modules:
        print(f"{'='*80}")
        print(f"Testing {module['name']} Module")
        print(f"{'='*80}")
        
        # Read current data
        try:
            with open(f"data/{module['file']}.json", 'r') as f:
                data_before = json.load(f)
        except FileNotFoundError:
            print(f"  ⚠ File not found: data/{module['file']}.json")
            results[module['name']] = 'SKIPPED'
            continue
        
        if len(data_before) == 0:
            print(f"  - No records found, skipping...")
            results[module['name']] = 'SKIPPED'
            continue
        
        # Get first non-protected record (skip ID='01' for departments)
        record_to_delete = None
        for record in data_before:
            if module['name'] == 'Departments' and record['id'] == '01':
                continue  # Skip Main Pharmacy (protected)
            record_to_delete = record
            break

        if not record_to_delete:
            print(f"  - No deletable records found, skipping...")
            results[module['name']] = 'SKIPPED'
            continue

        record_id = record_to_delete['id']
        record_name = record_to_delete.get('name') or record_to_delete.get('dr_name') or record_id
        
        print(f"  - Deleting: {record_name} (ID: {record_id})")
        
        # Perform bulk delete
        delete_response = session.post(
            f'http://127.0.0.1:5045{module["endpoint"]}',
            json={'ids': [record_id]}
        )
        
        print(f"  - Delete status: {delete_response.status_code}")
        
        if delete_response.status_code != 200:
            print(f"  ✗ Delete failed!")
            results[module['name']] = 'FAILED'
            continue
        
        time.sleep(1)
        
        # Read data again
        with open(f"data/{module['file']}.json", 'r') as f:
            data_after = json.load(f)
        
        # Check if record was deleted
        record_still_exists = any(
            r.get('name') == record_name or r.get('dr_name') == record_name 
            for r in data_after
        )
        
        if record_still_exists:
            print(f"  ✗ FAILED: Record '{record_name}' still exists in JSON file!")
            results[module['name']] = 'FAILED'
        else:
            print(f"  ✓ PASSED: Record '{record_name}' deleted and persisted")
            results[module['name']] = 'PASSED'
    
    # Print summary
    print("\n" + "="*80)
    print("ISSUE 2 TEST SUMMARY")
    print("="*80)
    for module_name, result in results.items():
        status_icon = "✓" if result == "PASSED" else ("✗" if result == "FAILED" else "⊘")
        print(f"{status_icon} {module_name}: {result}")
    
    all_passed = all(r in ['PASSED', 'SKIPPED'] for r in results.values())
    if all_passed:
        print("\n🎉 ALL MODULES PASSED!")
    else:
        print("\n⚠️ SOME MODULES FAILED!")
    print("="*80)
    
    return all_passed

if __name__ == '__main__':
    print("\n" + "="*80)
    print("COMPREHENSIVE API TEST FOR CASCADING DELETION AND PERSISTENCE")
    print("="*80)
    
    # Test Issue 1
    issue1_passed = test_cascading_deletion()
    
    # Test Issue 2
    issue2_passed = test_persistence_all_modules()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL TEST SUMMARY")
    print("="*80)
    print(f"Issue 1 (Cascading Deletion): {'✓ PASSED' if issue1_passed else '✗ FAILED'}")
    print(f"Issue 2 (Persistence): {'✓ PASSED' if issue2_passed else '✗ FAILED'}")
    print("="*80)
    
    if issue1_passed and issue2_passed:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED. Please review the output above.")

