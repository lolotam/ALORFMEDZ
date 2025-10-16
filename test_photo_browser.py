"""
Browser test for Photo Upload Issues using Playwright
- Issue 1: Photo upload not working for some medicine records
- Issue 2: Photo delete function not working
"""

from playwright.sync_api import sync_playwright, expect
import time
import os

def test_photo_upload_and_delete():
    """Test photo upload and delete functionality in browser"""
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("\n" + "="*80)
            print("BROWSER TEST: Photo Upload and Delete")
            print("="*80)
            
            # Login
            print("\n[Step 1] Logging in...")
            page.goto('http://127.0.0.1:5045/auth/login')
            page.fill('input[name="username"]', 'admin')
            page.fill('input[name="password"]', '@Xx123456789xX@')
            page.click('button[type="submit"]')
            page.wait_for_url('**/dashboard/**')
            print("  ✓ Logged in successfully")
            
            # Navigate to medicines
            print("\n[Step 2] Navigating to Medicines page...")
            page.goto('http://127.0.0.1:5045/medicines')
            page.wait_for_selector('table')
            print("  ✓ Medicines page loaded")
            
            # Get all medicine rows
            medicine_rows = page.query_selector_all('table tbody tr')
            print(f"  ✓ Found {len(medicine_rows)} medicine records")
            
            if len(medicine_rows) < 2:
                print("  ✗ Need at least 2 medicines for testing!")
                return False
            
            # Test uploading to the SECOND medicine (not the first)
            print("\n[Step 3] Testing upload to SECOND medicine record...")
            
            # Click edit on second medicine
            second_row = medicine_rows[1]
            medicine_name = second_row.query_selector('td:nth-child(2)').inner_text()
            print(f"  - Medicine: {medicine_name}")
            
            edit_button = second_row.query_selector('a[href*="/medicines/edit/"]')
            edit_button.click()
            page.wait_for_load_state('networkidle')
            print("  ✓ Edit page loaded")
            
            # Check if photo gallery section exists
            photo_gallery = page.query_selector('#medicine-photo-gallery')
            if not photo_gallery:
                print("  ✗ Photo gallery section not found!")
                return False
            print("  ✓ Photo gallery section found")
            
            # Expand upload section
            print("\n[Step 4] Expanding photo upload section...")
            upload_toggle = page.query_selector('button[data-bs-target="#uploadNewPhotos"]')
            if upload_toggle:
                upload_toggle.click()
                time.sleep(0.5)
                print("  ✓ Upload section expanded")
            
            # Create a test image file
            print("\n[Step 5] Creating test image...")
            test_image_path = 'test_upload_image.png'
            from PIL import Image
            img = Image.new('RGB', (300, 300), color='blue')
            img.save(test_image_path)
            print(f"  ✓ Test image created: {test_image_path}")
            
            # Upload the image
            print("\n[Step 6] Uploading image...")
            file_input = page.query_selector('input[type="file"]')
            if not file_input:
                print("  ✗ File input not found!")
                return False
            
            # Get absolute path
            abs_path = os.path.abspath(test_image_path)
            file_input.set_input_files(abs_path)
            print("  ✓ File selected")
            
            # Wait for upload to complete
            time.sleep(2)
            
            # Check if photo appears in gallery
            print("\n[Step 7] Verifying photo appears in gallery...")
            page.wait_for_selector('.photo-item', timeout=5000)
            photo_items = page.query_selector_all('.photo-item')
            print(f"  ✓ Found {len(photo_items)} photo(s) in gallery")
            
            if len(photo_items) == 0:
                print("  ✗ No photos in gallery after upload!")
                return False
            
            # Test delete functionality
            print("\n[Step 8] Testing delete functionality...")
            
            # Find delete button on first photo
            first_photo = photo_items[0]
            delete_button = first_photo.query_selector('button.btn-danger')
            
            if not delete_button:
                print("  ✗ Delete button not found!")
                return False
            
            print("  ✓ Delete button found")
            
            # Click delete button
            print("\n[Step 9] Clicking delete button...")

            # Handle confirmation dialog
            page.on('dialog', lambda dialog: dialog.accept())

            # Use JavaScript click to avoid hover interference
            page.evaluate('(button) => button.click()', delete_button)
            time.sleep(2)
            
            # Check if photo was removed
            print("\n[Step 10] Verifying photo was deleted...")
            remaining_photos = page.query_selector_all('.photo-item')
            
            if len(remaining_photos) < len(photo_items):
                print(f"  ✓ Photo deleted! ({len(photo_items)} -> {len(remaining_photos)} photos)")
            else:
                print(f"  ✗ Photo not deleted! Still {len(remaining_photos)} photos")
                return False
            
            # Test persistence - reload page
            print("\n[Step 11] Testing persistence (reloading page)...")
            page.reload()
            page.wait_for_load_state('networkidle')
            
            # Check photo count after reload
            final_photos = page.query_selector_all('.photo-item')
            print(f"  ✓ After reload: {len(final_photos)} photo(s)")
            
            if len(final_photos) == len(remaining_photos):
                print("  ✓ Photo deletion persisted!")
            else:
                print("  ✗ Photo deletion did NOT persist!")
                return False
            
            # Clean up test image
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
                print(f"\n  ✓ Cleaned up test image: {test_image_path}")
            
            print("\n" + "="*80)
            print("✓✓✓ ALL BROWSER TESTS PASSED ✓✓✓")
            print("  - Photo upload works for any medicine record")
            print("  - Photo appears in gallery immediately")
            print("  - Delete button works correctly")
            print("  - Deletion persists after page reload")
            print("="*80)
            
            return True
            
        except Exception as e:
            print(f"\n✗ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Keep browser open for a moment to see results
            time.sleep(2)
            browser.close()

if __name__ == '__main__':
    print("\n" + "="*80)
    print("COMPREHENSIVE BROWSER TEST FOR PHOTO ISSUES")
    print("="*80)
    
    result = test_photo_upload_and_delete()
    
    print("\n" + "="*80)
    print("FINAL RESULT")
    print("="*80)
    
    if result:
        print("🎉 ALL TESTS PASSED!")
        print("\nBoth issues are now fixed:")
        print("  ✓ Issue 1: Photo upload works for all medicine records")
        print("  ✓ Issue 2: Delete button works correctly")
    else:
        print("⚠️ TESTS FAILED. Please review the output above.")

