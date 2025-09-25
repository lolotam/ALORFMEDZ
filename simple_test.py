#!/usr/bin/env python3
"""
Simple test for store-department relationship functionality
"""

import json
from datetime import datetime

def load_data(filename):
    """Load data from JSON file"""
    try:
        with open(f'data/{filename}.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def test_data_integrity():
    """Test that data files are intact and contain expected data"""
    print("Testing data integrity...")

    # Load all data
    stores = load_data('stores')
    departments = load_data('departments')
    users = load_data('users')
    transfers = load_data('transfers')

    print(f"Stores: {len(stores)}")
    print(f"Departments: {len(departments)}")
    print(f"Users: {len(users)}")
    print(f"Transfers: {len(transfers)}")

    # Check if ICU store (03) exists
    icu_store = next((s for s in stores if s['id'] == '03'), None)
    if icu_store:
        print(f"ICU Store found: {icu_store['name']}")
        print(f"ICU Store inventory: {icu_store.get('inventory', {})}")
        print(f"ICU Store department: {icu_store.get('department_id')}")
    else:
        print("ICU Store not found")

    # Check if ICU department (03) exists
    icu_dept = next((d for d in departments if d['id'] == '03'), None)
    if icu_dept:
        print(f"ICU Department found: {icu_dept['name']}")
    else:
        print("ICU Department not found")

    # Check main store inventory
    main_store = next((s for s in stores if s['id'] == '01'), None)
    if main_store:
        print(f"Main Store inventory: {main_store.get('inventory', {})}")

    return True

def test_readonly_template():
    """Check if store edit template has readonly department field"""
    print("\nTesting store edit template...")

    try:
        with open('templates/stores/edit.html', 'r') as f:
            template_content = f.read()

        if 'readonly' in template_content:
            print("Template contains readonly field: YES")
        else:
            print("Template contains readonly field: NO")

        if 'department_name' in template_content:
            print("Template references department_name: YES")
        else:
            print("Template references department_name: NO")

        return True
    except FileNotFoundError:
        print("Store edit template not found")
        return False

def main():
    print("=" * 50)
    print("SIMPLE STORE-DEPARTMENT RELATIONSHIP TEST")
    print("=" * 50)

    # Test 1: Data integrity
    test_data_integrity()

    # Test 2: Template check
    test_readonly_template()

    print("\n" + "=" * 50)
    print("Manual verification needed:")
    print("1. Visit http://127.0.0.1:5045/stores/edit/03")
    print("2. Check if department field is readonly and shows 'Intensive Care Unit'")
    print("3. Try deleting store 03 and verify cascading delete works")
    print("4. Try recreating the department and verify stores are unaffected")
    print("=" * 50)

if __name__ == "__main__":
    main()