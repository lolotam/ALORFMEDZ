#!/usr/bin/env python3
"""
Test script for enhanced store-department relationship functionality
Tests cascading operations and inventory transfers
"""

import json
import sys
import time
import requests
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:5045"
session = requests.Session()

def load_data(filename):
    """Load data from JSON file"""
    try:
        with open(f'data/{filename}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(filename, data):
    """Save data to JSON file"""
    with open(f'data/{filename}.json', 'w') as f:
        json.dump(data, f, indent=2)

def print_status(message):
    """Print status message with timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def login_as_admin():
    """Login as admin user"""
    print_status("Logging in as admin...")
    login_data = {
        'username': 'admin',
        'password': '@Xx123456789xX@'
    }
    response = session.post(f'{BASE_URL}/auth/login', data=login_data)
    if response.status_code == 200 and 'Dashboard' in response.text:
        print_status("[OK] Admin login successful")
        return True
    else:
        print_status("[FAIL] Admin login failed")
        return False

def create_test_department_with_user():
    """Create a test department with user for testing"""
    print_status("Creating test department with user...")

    # Add a user for department 03 (ICU) to test cascading delete
    users = load_data('users')
    test_user = {
        "id": "99",  # Temporary test user
        "username": "test_icu_user",
        "password": "test123",
        "role": "department_user",
        "name": "Test ICU User",
        "email": "test_icu@hospital.com",
        "department_id": "03",
        "created_at": datetime.now().isoformat()
    }
    users.append(test_user)
    save_data('users', users)
    print_status("[OK] Test user created for ICU department")
    return test_user

def test_store_edit_readonly_department():
    """Test that store edit form shows readonly department field"""
    print_status("Testing store edit form readonly department field...")

    response = session.get(f'{BASE_URL}/stores/edit/03')
    if response.status_code == 200:
        # Check if department field is readonly
        if 'readonly' in response.text and 'Intensive Care Unit' in response.text:
            print_status("✅ Store edit form shows readonly department field correctly")
            return True
        else:
            print_status("❌ Store edit form does not show readonly department field")
            return False
    else:
        print_status(f"❌ Failed to access store edit form: {response.status_code}")
        return False

def test_store_cascading_delete():
    """Test store deletion with cascading delete of department and user"""
    print_status("Testing store cascading delete functionality...")

    # Check initial state
    stores_before = load_data('stores')
    departments_before = load_data('departments')
    users_before = load_data('users')
    transfers_before = load_data('transfers')

    print_status(f"Initial state: {len(stores_before)} stores, {len(departments_before)} departments, {len(users_before)} users")

    # Find ICU store, department, and user
    icu_store = next((s for s in stores_before if s['id'] == '03'), None)
    icu_dept = next((d for d in departments_before if d['id'] == '03'), None)
    icu_user = next((u for u in users_before if u.get('department_id') == '03'), None)

    if not icu_store:
        print_status("❌ ICU store not found")
        return False

    initial_inventory = icu_store.get('inventory', {})
    print_status(f"ICU store has inventory: {initial_inventory}")

    # Delete ICU store (should cascade delete department and user)
    response = session.get(f'{BASE_URL}/stores/delete/03')

    if response.status_code == 200 or response.status_code == 302:
        print_status("Store deletion request completed")

        # Check final state
        stores_after = load_data('stores')
        departments_after = load_data('departments')
        users_after = load_data('users')
        transfers_after = load_data('transfers')

        print_status(f"Final state: {len(stores_after)} stores, {len(departments_after)} departments, {len(users_after)} users")

        # Verify ICU store is deleted
        icu_store_after = next((s for s in stores_after if s['id'] == '03'), None)
        if icu_store_after:
            print_status("❌ ICU store was not deleted")
            return False
        else:
            print_status("✅ ICU store was deleted")

        # Verify ICU department is deleted
        icu_dept_after = next((d for d in departments_after if d['id'] == '03'), None)
        if icu_dept_after:
            print_status("❌ ICU department was not deleted")
            return False
        else:
            print_status("✅ ICU department was deleted (cascading delete)")

        # Verify ICU user is deleted (if existed)
        icu_user_after = next((u for u in users_after if u.get('department_id') == '03'), None)
        if icu_user_after:
            print_status("❌ ICU user was not deleted")
            return False
        else:
            print_status("✅ ICU user was deleted (cascading delete)")

        # Verify inventory was transferred to main store
        main_store_after = next((s for s in stores_after if s['id'] == '01'), None)
        if main_store_after and initial_inventory:
            main_inventory = main_store_after.get('inventory', {})
            transferred_correctly = True
            for med_id, qty in initial_inventory.items():
                if main_inventory.get(med_id, 0) >= qty:
                    print_status(f"✅ Medicine {med_id} inventory transferred correctly")
                else:
                    print_status(f"❌ Medicine {med_id} inventory not transferred correctly")
                    transferred_correctly = False

            if transferred_correctly:
                print_status("✅ All inventory transferred to main store")
            else:
                return False

        # Verify transfer record was created
        if len(transfers_after) > len(transfers_before):
            latest_transfer = transfers_after[-1]
            if (latest_transfer.get('source_store_id') == '03' and
                latest_transfer.get('destination_store_id') == '01'):
                print_status("✅ Transfer record created for inventory movement")
            else:
                print_status("❌ Transfer record not created correctly")
                return False
        else:
            print_status("❌ No transfer record created")
            return False

        return True
    else:
        print_status(f"❌ Store deletion failed: {response.status_code}")
        return False

def test_department_delete_without_affecting_stores():
    """Test that department deletion doesn't affect stores"""
    print_status("Testing department deletion without affecting stores...")

    # First, recreate ICU department (to test the user's requirement)
    departments = load_data('departments')
    icu_department = {
        "id": "03",
        "name": "Intensive Care Unit",
        "description": "Critical care and life support",
        "responsible_person": "ICU Manager",
        "telephone": "+1-555-ICU01",
        "notes": "Life-saving medications - Recreated",
        "created_at": datetime.now().isoformat()
    }
    departments.append(icu_department)
    save_data('departments', departments)
    print_status("✅ ICU department recreated successfully")

    # Create a new store for this department
    stores = load_data('stores')
    icu_store = {
        "id": "05",  # New store ID
        "name": "ICU Store - Recreated",
        "department_id": "03",
        "location": "Building B, Floor 4",
        "description": "Recreated ICU store",
        "inventory": {"01": 10},
        "created_at": datetime.now().isoformat()
    }
    stores.append(icu_store)
    save_data('stores', stores)
    print_status("✅ New ICU store created")

    # Now test deleting the department without affecting the store
    stores_before = load_data('stores')
    departments_before = load_data('departments')

    # Delete the department through the web interface
    response = session.get(f'{BASE_URL}/departments/delete/03')

    if response.status_code == 200 or response.status_code == 302:
        stores_after = load_data('stores')
        departments_after = load_data('departments')

        # Verify department is deleted
        icu_dept_after = next((d for d in departments_after if d['id'] == '03'), None)
        if icu_dept_after:
            print_status("❌ ICU department was not deleted")
            return False
        else:
            print_status("✅ ICU department was deleted")

        # Verify store remains unaffected
        icu_store_after = next((s for s in stores_after if s['id'] == '05'), None)
        if not icu_store_after:
            print_status("❌ ICU store was incorrectly deleted")
            return False
        else:
            print_status("✅ ICU store remains unaffected by department deletion")

        return True
    else:
        print_status(f"❌ Department deletion failed: {response.status_code}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    print_status("Cleaning up test data...")

    # Remove test user
    users = load_data('users')
    users = [u for u in users if u['id'] != '99']
    save_data('users', users)

    # Remove test store
    stores = load_data('stores')
    stores = [s for s in stores if s['id'] != '05']
    save_data('stores', stores)

    print_status("✅ Test data cleaned up")

def main():
    """Main test function"""
    print("="*60)
    print("STORE-DEPARTMENT RELATIONSHIP ENHANCEMENT TEST")
    print("="*60)

    # Wait for server to start
    print_status("Waiting for server to start...")
    time.sleep(3)

    # Test login
    if not login_as_admin():
        print_status("❌ Cannot proceed without admin access")
        sys.exit(1)

    # Create test data
    create_test_department_with_user()

    # Run tests
    tests_passed = 0
    total_tests = 3

    print_status("Starting tests...")

    # Test 1: Store edit readonly department field
    if test_store_edit_readonly_department():
        tests_passed += 1

    # Test 2: Store cascading delete
    if test_store_cascading_delete():
        tests_passed += 1

    # Test 3: Department delete without affecting stores
    if test_department_delete_without_affecting_stores():
        tests_passed += 1

    # Cleanup
    cleanup_test_data()

    # Results
    print("="*60)
    print(f"TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    print("="*60)

    if tests_passed == total_tests:
        print_status("🎉 ALL TESTS PASSED! Store-department relationship enhancements work correctly")
        print("\n✅ Verified functionality:")
        print("  • Department field auto-populated and non-editable in store edit")
        print("  • Store deletion cascades to remove department and assigned users")
        print("  • Department deletion does not affect stores (allows recreation)")
        print("  • Inventory transferred to main store with transfer records")
        sys.exit(0)
    else:
        print_status("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)

if __name__ == "__main__":
    main()