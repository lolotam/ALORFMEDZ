"""
Photo Upload Utility Functions
"""

import os
import uuid
import hashlib
from datetime import datetime
from PIL import Image
from werkzeug.utils import secure_filename

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
MAX_IMAGE_SIZE = (2048, 2048)  # Max width/height
THUMBNAIL_SIZE = (300, 300)

def ensure_upload_directory():
    """Ensure upload directories exist"""
    directories = [
        UPLOAD_FOLDER,
        os.path.join(UPLOAD_FOLDER, 'medicines'),
        os.path.join(UPLOAD_FOLDER, 'patients'),
        os.path.join(UPLOAD_FOLDER, 'suppliers'),
        os.path.join(UPLOAD_FOLDER, 'departments'),
        os.path.join(UPLOAD_FOLDER, 'profiles'),
        os.path.join(UPLOAD_FOLDER, 'thumbnails')
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Generate unique filename while preserving extension"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    return f"{timestamp}_{unique_id}.{extension}"

def calculate_file_hash(file_path):
    """Calculate MD5 hash of file for duplicate detection"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def resize_image(image_path, max_size=MAX_IMAGE_SIZE, quality=85):
    """Resize image if it exceeds max dimensions"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Check if resize is needed
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(image_path, 'JPEG', quality=quality, optimize=True)
                return True
            return False
    except Exception as e:
        raise Exception(f"Error resizing image: {str(e)}")

def create_thumbnail(image_path, thumbnail_path, size=THUMBNAIL_SIZE):
    """Create thumbnail for image"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=80, optimize=True)
            return True
    except Exception as e:
        raise Exception(f"Error creating thumbnail: {str(e)}")

def save_uploaded_photo(file, category, entity_id=None):
    """
    Save uploaded photo with processing

    Args:
        file: FileStorage object from request.files
        category: Category folder (medicines, patients, suppliers, departments)
        entity_id: Optional entity ID for filename prefix

    Returns:
        dict with photo info or None if failed
    """
    try:
        if not file or file.filename == '':
            return None

        if not allowed_file(file.filename):
            raise ValueError(f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB")

        # Ensure directories exist
        ensure_upload_directory()

        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)

        # Add entity ID prefix if provided
        if entity_id:
            name_part, ext_part = unique_filename.rsplit('.', 1)
            unique_filename = f"{entity_id}_{name_part}.{ext_part}"

        # Create file paths
        category_folder = os.path.join(UPLOAD_FOLDER, category)
        file_path = os.path.join(category_folder, unique_filename)

        # Save original file
        file.save(file_path)

        # Process image
        resized = resize_image(file_path)

        # Create thumbnail
        thumbnail_filename = f"thumb_{unique_filename}"
        thumbnail_path = os.path.join(UPLOAD_FOLDER, 'thumbnails', thumbnail_filename)
        create_thumbnail(file_path, thumbnail_path)

        # Calculate file hash for duplicate detection
        file_hash = calculate_file_hash(file_path)

        # Get final file size
        final_size = os.path.getsize(file_path)

        return {
            'filename': unique_filename,
            'original_filename': original_filename,
            'file_path': file_path.replace('\\', '/'),
            'url': f"/{file_path.replace(chr(92), '/')}",
            'thumbnail_filename': thumbnail_filename,
            'thumbnail_path': thumbnail_path.replace('\\', '/'),
            'thumbnail_url': f"/{thumbnail_path.replace(chr(92), '/')}",
            'category': category,
            'entity_id': entity_id,
            'file_size': final_size,
            'file_hash': file_hash,
            'resized': resized,
            'upload_date': datetime.now().isoformat()
        }

    except Exception as e:
        # Clean up files if they were created
        for path in [locals().get('file_path'), locals().get('thumbnail_path')]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass
        raise e

def delete_photo(photo_info):
    """Delete photo and thumbnail files"""
    try:
        deleted_files = []

        # Delete main file
        if photo_info.get('file_path') and os.path.exists(photo_info['file_path']):
            os.remove(photo_info['file_path'])
            deleted_files.append(photo_info['file_path'])

        # Delete thumbnail
        if photo_info.get('thumbnail_path') and os.path.exists(photo_info['thumbnail_path']):
            os.remove(photo_info['thumbnail_path'])
            deleted_files.append(photo_info['thumbnail_path'])

        return deleted_files

    except Exception as e:
        raise Exception(f"Error deleting photo files: {str(e)}")

def get_photo_info(filename, category):
    """Get photo information from filename and category"""
    file_path = os.path.join(UPLOAD_FOLDER, category, filename)
    if not os.path.exists(file_path):
        return None

    # Check for thumbnail
    thumbnail_filename = f"thumb_{filename}"
    thumbnail_path = os.path.join(UPLOAD_FOLDER, 'thumbnails', thumbnail_filename)

    return {
        'filename': filename,
        'file_path': file_path.replace('\\', '/'),
        'url': f"/{file_path.replace('\\', '/')}",
        'thumbnail_filename': thumbnail_filename if os.path.exists(thumbnail_path) else None,
        'thumbnail_path': thumbnail_path.replace('\\', '/') if os.path.exists(thumbnail_path) else None,
        'thumbnail_url': f"/{thumbnail_path.replace('\\', '/')}" if os.path.exists(thumbnail_path) else None,
        'category': category,
        'file_size': os.path.getsize(file_path),
        'exists': True
    }

def validate_upload_request(request, max_files=5):
    """Validate upload request and return file list"""
    if 'photo' not in request.files:
        raise ValueError("No photo file in request")

    files = request.files.getlist('photo')
    if not files or all(f.filename == '' for f in files):
        raise ValueError("No files selected")

    if len(files) > max_files:
        raise ValueError(f"Too many files. Maximum {max_files} files allowed")

    return files

def cleanup_old_uploads(days=30):
    """Clean up uploads older than specified days"""
    cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
    deleted_count = 0

    try:
        for root, dirs, files in os.walk(UPLOAD_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < cutoff_date:
                    os.remove(file_path)
                    deleted_count += 1

        return deleted_count
    except Exception as e:
        raise Exception(f"Error cleaning up uploads: {str(e)}")