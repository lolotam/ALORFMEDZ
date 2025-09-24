"""
Photos Management Blueprint
"""

from flask import Blueprint, request, jsonify, session, send_file
import os
from utils.helpers import login_required, admin_required
from utils.upload import save_uploaded_photo, delete_photo, get_photo_info, validate_upload_request, cleanup_old_uploads
from utils.database import log_activity

photos_bp = Blueprint('photos', __name__)

@photos_bp.route('/upload/<category>', methods=['POST'])
@login_required
def upload_photo(category):
    """Upload photo for specified category"""
    try:
        # Validate category
        allowed_categories = ['medicines', 'patients', 'suppliers', 'departments', 'profiles']
        if category not in allowed_categories:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400

        # Validate request
        files = validate_upload_request(request, max_files=1)
        file = files[0]

        # Get entity ID if provided
        entity_id = request.form.get('entity_id')

        # Save photo
        photo_info = save_uploaded_photo(file, category, entity_id)

        if photo_info:
            # Log activity
            log_activity(
                action='upload_photo',
                entity_type=category,
                details={
                    'filename': photo_info['filename'],
                    'entity_id': entity_id,
                    'file_size': photo_info['file_size']
                }
            )

            return jsonify({
                'success': True,
                'message': 'Photo uploaded successfully',
                'photo': photo_info
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Upload failed'}), 400

    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload error: {str(e)}'}), 500

@photos_bp.route('/upload/<category>/multiple', methods=['POST'])
@login_required
def upload_multiple_photos(category):
    """Upload multiple photos for specified category"""
    try:
        # Validate category
        allowed_categories = ['medicines', 'patients', 'suppliers', 'departments', 'profiles']
        if category not in allowed_categories:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400

        # Validate request
        files = validate_upload_request(request, max_files=5)

        # Get entity ID if provided
        entity_id = request.form.get('entity_id')

        uploaded_photos = []
        failed_uploads = []

        for file in files:
            try:
                photo_info = save_uploaded_photo(file, category, entity_id)
                if photo_info:
                    uploaded_photos.append(photo_info)
                else:
                    failed_uploads.append(file.filename)
            except Exception as e:
                failed_uploads.append(f"{file.filename}: {str(e)}")

        # Log activity
        if uploaded_photos:
            log_activity(
                action='upload_multiple_photos',
                entity_type=category,
                details={
                    'count': len(uploaded_photos),
                    'entity_id': entity_id,
                    'failed_count': len(failed_uploads)
                }
            )

        if uploaded_photos:
            response = {
                'success': True,
                'message': f'Uploaded {len(uploaded_photos)} photos successfully',
                'photos': uploaded_photos
            }
            if failed_uploads:
                response['warnings'] = failed_uploads
            return jsonify(response), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No photos uploaded successfully',
                'errors': failed_uploads
            }), 400

    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload error: {str(e)}'}), 500

@photos_bp.route('/delete/<category>/<filename>', methods=['DELETE'])
@login_required
def delete_photo_route(category, filename):
    """Delete photo by filename and category"""
    try:
        # Validate category
        allowed_categories = ['medicines', 'patients', 'suppliers', 'departments', 'profiles']
        if category not in allowed_categories:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400

        # Get photo info
        photo_info = get_photo_info(filename, category)
        if not photo_info or not photo_info.get('exists'):
            return jsonify({'success': False, 'message': 'Photo not found'}), 404

        # Delete photo files
        deleted_files = delete_photo(photo_info)

        # Log activity
        log_activity(
            action='delete_photo',
            entity_type=category,
            details={
                'filename': filename,
                'deleted_files': deleted_files
            }
        )

        return jsonify({
            'success': True,
            'message': 'Photo deleted successfully',
            'deleted_files': deleted_files
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Delete error: {str(e)}'}), 500

@photos_bp.route('/info/<category>/<filename>')
@login_required
def get_photo_info_route(category, filename):
    """Get photo information"""
    try:
        # Validate category
        allowed_categories = ['medicines', 'patients', 'suppliers', 'departments', 'profiles']
        if category not in allowed_categories:
            return jsonify({'success': False, 'message': 'Invalid category'}), 400

        photo_info = get_photo_info(filename, category)
        if not photo_info or not photo_info.get('exists'):
            return jsonify({'success': False, 'message': 'Photo not found'}), 404

        return jsonify({
            'success': True,
            'photo': photo_info
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting photo info: {str(e)}'}), 500

@photos_bp.route('/view/<category>/<filename>')
@login_required
def view_photo(category, filename):
    """View/serve photo file"""
    try:
        # Validate category
        allowed_categories = ['medicines', 'patients', 'suppliers', 'departments', 'profiles']
        if category not in allowed_categories:
            return jsonify({'error': 'Invalid category'}), 400

        photo_info = get_photo_info(filename, category)
        if not photo_info or not photo_info.get('exists'):
            return jsonify({'error': 'Photo not found'}), 404

        return send_file(photo_info['file_path'])

    except Exception as e:
        return jsonify({'error': f'Error serving photo: {str(e)}'}), 500

@photos_bp.route('/thumbnail/<filename>')
@login_required
def view_thumbnail(filename):
    """View/serve thumbnail file"""
    try:
        thumbnail_path = os.path.join('static', 'uploads', 'thumbnails', filename)
        if not os.path.exists(thumbnail_path):
            return jsonify({'error': 'Thumbnail not found'}), 404

        return send_file(thumbnail_path)

    except Exception as e:
        return jsonify({'error': f'Error serving thumbnail: {str(e)}'}), 500

@photos_bp.route('/cleanup', methods=['POST'])
@admin_required
def cleanup_old_photos():
    """Clean up old uploaded photos (admin only)"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 30)

        # Validate days parameter
        if not isinstance(days, int) or days < 1:
            return jsonify({'success': False, 'message': 'Invalid days parameter'}), 400

        deleted_count = cleanup_old_uploads(days)

        # Log activity
        log_activity(
            action='cleanup_photos',
            entity_type='system',
            details={
                'days_threshold': days,
                'deleted_count': deleted_count
            }
        )

        return jsonify({
            'success': True,
            'message': f'Cleaned up {deleted_count} old photos',
            'deleted_count': deleted_count
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Cleanup error: {str(e)}'}), 500

@photos_bp.route('/stats')
@login_required
def get_upload_stats():
    """Get upload statistics"""
    try:
        from utils.upload import UPLOAD_FOLDER

        stats = {
            'categories': {},
            'total_files': 0,
            'total_size': 0
        }

        categories = ['medicines', 'patients', 'suppliers', 'departments', 'profiles', 'thumbnails']

        for category in categories:
            category_path = os.path.join(UPLOAD_FOLDER, category)
            if os.path.exists(category_path):
                files = os.listdir(category_path)
                file_count = len(files)

                category_size = 0
                for file in files:
                    file_path = os.path.join(category_path, file)
                    if os.path.isfile(file_path):
                        category_size += os.path.getsize(file_path)

                stats['categories'][category] = {
                    'file_count': file_count,
                    'size_bytes': category_size,
                    'size_mb': round(category_size / (1024 * 1024), 2)
                }

                if category != 'thumbnails':  # Don't count thumbnails in total
                    stats['total_files'] += file_count
                    stats['total_size'] += category_size
            else:
                stats['categories'][category] = {
                    'file_count': 0,
                    'size_bytes': 0,
                    'size_mb': 0
                }

        stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error getting stats: {str(e)}'}), 500