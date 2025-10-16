"""
Test script for Photo Upload Issues
- Issue 1: Photo upload not working for some medicine records
- Issue 2: Photo delete function not working
"""

import requests
import json
from PIL import Image
import io

def create_test_image(color='red'):
    """Create a test image in memory"""
    # Create a simple 200x200 image
    img = Image.new('RGB', (200, 200), color=color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_upload_multiple_medicines():
    """Test Issue 1: Upload photos to multiple medicine records"""
    print("\n" + "="*80)
    print("TESTING ISSUE 1: Photo Upload for Multiple Medicine Records")
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
    
    # Get multiple medicines to test with
    print("\n[Step 1] Getting medicines to test with...")
    with open('data/medicines.json', 'r') as f:
        medicines = json.load(f)
    
    if len(medicines) < 3:
        print("  ✗ Need at least 3 medicines for testing!")
        return False
    
    # Test with first 3 medicines
    test_medicines = medicines[:3]
    print(f"  ✓ Testing with {len(test_medicines)} medicines:")
    for med in test_medicines:
        print(f"    - {med['name']} (ID: {med['id']})")
    
    # Upload photos to each medicine
    colors = ['red', 'green', 'blue']
    uploaded_photos = {}
    
    for i, medicine in enumerate(test_medicines):
        medicine_id = medicine['id']
        medicine_name = medicine['name']
        color = colors[i]
        
        print(f"\n[Step 2.{i+1}] Uploading {color} photo to {medicine_name} (ID: {medicine_id})...")
        
        # Create test image
        test_image = create_test_image(color)
        
        # Upload photo
        files = {'photo': (f'test_{color}.png', test_image, 'image/png')}
        data = {'entity_id': medicine_id}
        
        upload_response = session.post(
            'http://127.0.0.1:5045/photos/upload/medicines',
            files=files,
            data=data
        )
        
        print(f"  - Upload status: {upload_response.status_code}")
        
        if upload_response.status_code != 200:
            print(f"  ✗ Upload failed for medicine {medicine_id}!")
            print(f"  Response: {upload_response.text}")
            return False
        
        upload_result = upload_response.json()
        
        if not upload_result.get('success'):
            print(f"  ✗ Upload failed: {upload_result.get('message')}")
            return False
        
        photo_info = upload_result.get('photo', {})
        uploaded_filename = photo_info.get('filename')
        
        print(f"  ✓ Photo uploaded: {uploaded_filename}")
        
        # Store for later verification
        uploaded_photos[medicine_id] = uploaded_filename
    
    # Verify all photos are accessible
    print(f"\n[Step 3] Verifying all uploaded photos are accessible...")
    
    for medicine_id, filename in uploaded_photos.items():
        # List photos for this medicine
        list_response = session.get(
            f'http://127.0.0.1:5045/photos/list/medicines?entity_id={medicine_id}'
        )
        
        if list_response.status_code != 200:
            print(f"  ✗ Failed to list photos for medicine {medicine_id}")
            return False
        
        list_result = list_response.json()
        
        if not list_result.get('success'):
            print(f"  ✗ List failed for medicine {medicine_id}")
            return False
        
        photos = list_result.get('photos', [])
        
        # Check if our uploaded photo is in the list
        found = any(p.get('filename') == filename for p in photos)
        
        if found:
            print(f"  ✓ Medicine {medicine_id}: Photo {filename} found in gallery")
        else:
            print(f"  ✗ Medicine {medicine_id}: Photo {filename} NOT found in gallery!")
            return False
    
    print("\n" + "="*80)
    print("✓✓✓ ISSUE 1 TEST PASSED ✓✓✓")
    print("  - Photos uploaded successfully to all medicine records")
    print("  - All photos are accessible via API")
    print("="*80)
    
    return True, uploaded_photos

def test_delete_functionality(uploaded_photos):
    """Test Issue 2: Photo delete functionality"""
    print("\n" + "="*80)
    print("TESTING ISSUE 2: Photo Delete Functionality")
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
    
    # Test deleting one photo
    if not uploaded_photos:
        print("  ✗ No uploaded photos to test deletion!")
        return False
    
    # Get first medicine ID and filename
    medicine_id = list(uploaded_photos.keys())[0]
    filename = uploaded_photos[medicine_id]
    
    print(f"\n[Step 1] Deleting photo {filename} from medicine {medicine_id}...")
    
    # Delete photo
    delete_response = session.delete(
        f'http://127.0.0.1:5045/photos/delete/medicines/{filename}'
    )
    
    print(f"  - Delete status: {delete_response.status_code}")
    
    if delete_response.status_code != 200:
        print(f"  ✗ Delete failed!")
        print(f"  Response: {delete_response.text}")
        return False
    
    delete_result = delete_response.json()
    
    if not delete_result.get('success'):
        print(f"  ✗ Delete failed: {delete_result.get('message')}")
        return False
    
    print(f"  ✓ Photo deleted successfully")
    
    # Verify photo is removed from gallery
    print(f"\n[Step 2] Verifying photo is removed from gallery...")
    
    list_response = session.get(
        f'http://127.0.0.1:5045/photos/list/medicines?entity_id={medicine_id}'
    )
    
    if list_response.status_code != 200:
        print(f"  ✗ Failed to list photos")
        return False
    
    list_result = list_response.json()
    photos = list_result.get('photos', [])
    
    # Check if deleted photo is still in the list
    still_exists = any(p.get('filename') == filename for p in photos)
    
    if still_exists:
        print(f"  ✗ Photo still exists in gallery after deletion!")
        return False
    else:
        print(f"  ✓ Photo successfully removed from gallery")
    
    print("\n" + "="*80)
    print("✓✓✓ ISSUE 2 TEST PASSED (API Level) ✓✓✓")
    print("  - Photo deleted successfully via API")
    print("  - Photo removed from gallery")
    print("  ⚠ Note: JavaScript delete button issue needs separate fix")
    print("="*80)
    
    return True

if __name__ == '__main__':
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST FOR PHOTO UPLOAD ISSUES")
    print("="*80)
    
    # Test Issue 1
    result = test_upload_multiple_medicines()
    if isinstance(result, tuple):
        issue1_passed, uploaded_photos = result
    else:
        issue1_passed = result
        uploaded_photos = {}
    
    # Test Issue 2
    issue2_passed = test_delete_functionality(uploaded_photos)
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL TEST SUMMARY")
    print("="*80)
    print(f"Issue 1 (Upload to Multiple Medicines): {'✓ PASSED' if issue1_passed else '✗ FAILED'}")
    print(f"Issue 2 (Delete Functionality - API): {'✓ PASSED' if issue2_passed else '✗ FAILED'}")
    print("="*80)
    
    if issue1_passed and issue2_passed:
        print("\n🎉 ALL API TESTS PASSED!")
        print("\n⚠️ JAVASCRIPT FIX NEEDED:")
        print("  - Delete button on thumbnails doesn't work (global reference issue)")
        print("  - Fix: Add global reference in PhotoGallery.init() method")
    else:
        print("\n⚠️ SOME TESTS FAILED. Please review the output above.")

