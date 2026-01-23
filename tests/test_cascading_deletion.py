"""
Comprehensive test for cascading deletion and bulk delete persistence
Tests Issue 1 (cascading deletion) and Issue 2 (persistence problem)
"""

from playwright.sync_api import sync_playwright
import time
import json

def login(page):
    """Login to the application"""
    page.goto('http://127.0.0.1:5045')
    page.fill('input[name="username"]', 'admin')
    page.fill('input[name="password"]', '@Xx123456789xX@')
    page.click('button[type="submit"]')
    time.sleep(2)  # Wait for login to complete

def test_cascading_deletion():
    """Test Issue 1: Cascading deletion of patients with consumption records"""
    print("\n" + "="*80)
    print("TESTING ISSUE 1: Cascading Deletion of Patients with Consumption Records")
    print("="*80)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Step 1: Login
            print("\n[Step 1] Logging in...")
            login(page)
            print("✓ Logged in successfully")
            
            # Step 2: Generate sample data first
            print("\n[Step 2] Generating sample data...")
            page.goto('http://127.0.0.1:5045/settings')
            time.sleep(1)
            
            # Click the generate sample data button (which now has modal)
            page.click('button:has-text("Generate Sample Data")')
            time.sleep(0.5)
            
            # Click "Yes, Proceed" in the modal
            page.click('button:has-text("Yes, Proceed")')
            time.sleep(5)  # Wait for data generation
            print("✓ Sample data generated")
            
            # Step 3: Check initial data
            print("\n[Step 3] Checking initial data...")
            with open('data/patients.json', 'r') as f:
                patients_before = json.load(f)
            with open('data/consumption.json', 'r') as f:
                consumption_before = json.load(f)
            
            print(f"  - Patients: {len(patients_before)}")
            print(f"  - Consumption records: {len(consumption_before)}")
            
            if len(patients_before) == 0:
                print("✗ No patients found! Cannot test cascading deletion.")
                return False
            
            # Step 4: Navigate to Patients page
            print("\n[Step 4] Navigating to Patients page...")
            page.goto('http://127.0.0.1:5045/patients')
            time.sleep(1)
            print("✓ On Patients page")
            
            # Step 5: Select first patient for deletion
            checkboxes = page.locator('.bulk-select:not([disabled])')
            if checkboxes.count() == 0:
                print("✗ No checkboxes found!")
                return False
            
            selected_id = checkboxes.first.get_attribute('value')
            selected_row = page.locator(f'tr[data-id="{selected_id}"]')
            patient_name = selected_row.locator('td:nth-child(4) strong').text_content()
            
            # Count consumption records for this patient
            consumption_for_patient = sum(
                1 for record in consumption_before 
                if record.get('patient_id') == selected_id
            )
            
            print(f"\n[Step 5] Selecting patient ID: {selected_id}, Name: {patient_name}")
            print(f"  - This patient has {consumption_for_patient} consumption records")
            checkboxes.first.check()
            time.sleep(0.5)
            
            # Step 6: Click Delete Selected
            print("\n[Step 6] Clicking 'Delete Selected' button...")

            # Set up dialog handler BEFORE clicking
            page.on('dialog', lambda dialog: dialog.accept())

            delete_button = page.locator('button:has-text("Delete Selected")')
            delete_button.click()
            time.sleep(3)  # Wait for deletion to complete
            
            # Step 7: Check if deletion succeeded
            print("\n[Step 7] Checking deletion results...")
            
            # Wait for success message
            time.sleep(2)
            
            # Check JSON files
            with open('data/patients.json', 'r') as f:
                patients_after = json.load(f)
            with open('data/consumption.json', 'r') as f:
                consumption_after = json.load(f)
            
            print(f"  - Patients before: {len(patients_before)}, after: {len(patients_after)}")
            print(f"  - Consumption before: {len(consumption_before)}, after: {len(consumption_after)}")
            
            # Verify patient was deleted
            patient_deleted = len(patients_after) == len(patients_before) - 1
            patient_not_in_json = not any(p['name'] == patient_name for p in patients_after)
            
            # Verify consumption records were deleted
            consumption_deleted = len(consumption_after) == len(consumption_before) - consumption_for_patient
            
            if patient_deleted and patient_not_in_json:
                print(f"✓ Patient '{patient_name}' deleted successfully")
            else:
                print(f"✗ Patient '{patient_name}' NOT deleted!")
                return False
            
            if consumption_for_patient > 0:
                if consumption_deleted:
                    print(f"✓ {consumption_for_patient} consumption records deleted (cascading deletion worked!)")
                else:
                    print(f"✗ Consumption records NOT deleted! Expected {consumption_for_patient} deletions")
                    return False
            else:
                print("  - No consumption records to delete")
            
            # Step 8: Test persistence - navigate away and back
            print("\n[Step 8] Testing persistence...")
            page.goto('http://127.0.0.1:5045/dashboard')
            time.sleep(1)
            page.goto('http://127.0.0.1:5045/patients')
            time.sleep(1)
            
            # Check if patient reappeared
            all_patient_names = page.locator('table tbody tr td:nth-child(4) strong').all_text_contents()
            patient_reappeared = patient_name in all_patient_names
            
            if patient_reappeared:
                print(f"✗ PERSISTENCE ISSUE: Patient '{patient_name}' reappeared after navigation!")
                return False
            else:
                print(f"✓ Patient '{patient_name}' remains deleted after navigation")
            
            # Final verification from JSON
            with open('data/patients.json', 'r') as f:
                patients_final = json.load(f)
            
            if any(p['name'] == patient_name for p in patients_final):
                print(f"✗ CRITICAL: Patient '{patient_name}' still in JSON file!")
                return False
            else:
                print(f"✓ Patient '{patient_name}' permanently deleted from JSON file")
            
            print("\n" + "="*80)
            print("✓✓✓ ISSUE 1 TEST PASSED ✓✓✓")
            print("  - Cascading deletion works correctly")
            print("  - Consumption records deleted automatically")
            print("  - Deletion persists after navigation")
            print("="*80)
            
            time.sleep(3)
            return True
            
        except Exception as e:
            print(f"\n✗ TEST FAILED WITH ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()

def test_bulk_delete_persistence_all_modules():
    """Test Issue 2: Bulk delete persistence across all modules"""
    print("\n" + "="*80)
    print("TESTING ISSUE 2: Bulk Delete Persistence Across All Modules")
    print("="*80)
    
    modules_to_test = [
        {'name': 'Medicines', 'url': '/medicines', 'name_column': 3},
        {'name': 'Doctors', 'url': '/doctors', 'name_column': 2},
        {'name': 'Suppliers', 'url': '/suppliers', 'name_column': 2},
        {'name': 'Departments', 'url': '/departments', 'name_column': 2},
    ]
    
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Login
            print("\n[Step 1] Logging in...")
            login(page)
            print("✓ Logged in successfully")
            
            for module in modules_to_test:
                print(f"\n{'='*80}")
                print(f"Testing {module['name']} Module")
                print(f"{'='*80}")
                
                # Navigate to module
                page.goto(f"http://127.0.0.1:5045{module['url']}")
                time.sleep(1)
                
                # Check if there are any records
                checkboxes = page.locator('.bulk-select:not([disabled])')
                if checkboxes.count() == 0:
                    print(f"  - No records found in {module['name']}, skipping...")
                    results[module['name']] = 'SKIPPED'
                    continue
                
                # Select first record
                selected_id = checkboxes.first.get_attribute('value')
                selected_row = page.locator(f'tr[data-id="{selected_id}"]')
                item_name = selected_row.locator(f'td:nth-child({module["name_column"]}) strong').text_content()
                
                print(f"  - Selecting: {item_name} (ID: {selected_id})")
                checkboxes.first.check()
                time.sleep(0.5)

                # Set up dialog handler BEFORE clicking
                page.on('dialog', lambda dialog: dialog.accept())

                # Click delete
                delete_button = page.locator('button:has-text("Delete Selected")')
                delete_button.click()
                time.sleep(3)  # Wait for deletion to complete
                
                # Navigate away and back
                page.goto('http://127.0.0.1:5045/dashboard')
                time.sleep(1)
                page.goto(f"http://127.0.0.1:5045{module['url']}")
                time.sleep(1)
                
                # Check if item reappeared
                all_names = page.locator(f'table tbody tr td:nth-child({module["name_column"]}) strong').all_text_contents()
                item_reappeared = item_name in all_names
                
                if item_reappeared:
                    print(f"  ✗ FAILED: '{item_name}' reappeared after navigation!")
                    results[module['name']] = 'FAILED'
                else:
                    print(f"  ✓ PASSED: '{item_name}' remains deleted")
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
            
            time.sleep(3)
            return all_passed
            
        except Exception as e:
            print(f"\n✗ TEST FAILED WITH ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()

if __name__ == '__main__':
    print("\n" + "="*80)
    print("COMPREHENSIVE CASCADING DELETION AND PERSISTENCE TEST")
    print("="*80)
    
    # Test Issue 1: Cascading Deletion
    issue1_passed = test_cascading_deletion()
    
    # Test Issue 2: Persistence
    issue2_passed = test_bulk_delete_persistence_all_modules()
    
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

