/**
 * Photo Gallery Component
 * Displays uploaded photos with lightbox functionality
 */

class PhotoGallery {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.containerId = containerId;
        // Sanitize container ID for use in JavaScript identifiers (replace hyphens with underscores)
        this.safeContainerId = containerId.replace(/-/g, '_');
        this.options = {
            category: options.category || 'medicines',
            entityId: options.entityId || null,
            showThumbnails: options.showThumbnails !== false,
            allowDelete: options.allowDelete !== false,
            onDelete: options.onDelete || null,
            onError: options.onError || null
        };

        this.photos = [];

        this.init();
    }

    init() {
        if (!this.container) {
            console.error('Photo gallery container not found');
            return;
        }

        // Store global reference for onclick handlers (using sanitized ID)
        window[`photoGallery_${this.safeContainerId}`] = this;

        this.createGalleryArea();
        this.loadPhotos();
    }

    createGalleryArea() {
        this.container.innerHTML = `
            <div class="photo-gallery">
                <div class="gallery-grid row" id="${this.containerId}_grid">
                    <!-- Photos will be loaded here -->
                </div>
                <div class="gallery-empty text-center text-muted p-4 d-none" id="${this.containerId}_empty">
                    <i class="bi bi-images fs-1 opacity-50"></i>
                    <p class="mt-2">No photos uploaded yet</p>
                </div>
                <div class="gallery-loading text-center p-4" id="${this.containerId}_loading">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading photos...</p>
                </div>
            </div>
        `;

        this.gridContainer = document.getElementById(`${this.containerId}_grid`);
        this.emptyContainer = document.getElementById(`${this.containerId}_empty`);
        this.loadingContainer = document.getElementById(`${this.containerId}_loading`);
    }

    async loadPhotos() {
        try {
            this.showLoading(true);

            // Build API endpoint URL
            let url = `/photos/list/${this.options.category}`;
            if (this.options.entityId) {
                url += `?entity_id=${this.options.entityId}`;
            }

            const response = await fetch(url);
            const result = await response.json();

            if (result.success) {
                this.photos = result.photos || [];
            } else {
                throw new Error(result.message || 'Failed to load photos');
            }

            this.renderPhotos();
            this.showLoading(false);

        } catch (error) {
            this.showLoading(false);
            this.showError(`Failed to load photos: ${error.message}`);

            if (this.options.onError) {
                this.options.onError(error);
            }
        }
    }

    renderPhotos() {
        this.gridContainer.innerHTML = '';

        if (this.photos.length === 0) {
            this.emptyContainer.classList.remove('d-none');
            return;
        }

        this.emptyContainer.classList.add('d-none');

        this.photos.forEach((photo, index) => {
            const photoItem = this.createPhotoItem(photo, index);
            this.gridContainer.appendChild(photoItem);
        });
    }

    createPhotoItem(photo, index) {
        const colDiv = document.createElement('div');
        colDiv.className = 'col-6 col-md-4 col-lg-3 mb-3';

        const imageUrl = this.options.showThumbnails && photo.thumbnail_url
            ? photo.thumbnail_url
            : photo.url;

        colDiv.innerHTML = `
            <div class="photo-item position-relative">
                <img src="${imageUrl}"
                     class="img-fluid rounded shadow-sm photo-thumbnail"
                     style="width: 100%; height: 150px; object-fit: cover; cursor: pointer;"
                     onclick="photoGallery_${this.safeContainerId}.openLightbox(${index})"
                     alt="Photo ${index + 1}">

                ${this.options.allowDelete ? `
                <button type="button"
                        class="btn btn-sm btn-danger position-absolute top-0 end-0 rounded-circle"
                        style="width: 25px; height: 25px; margin: 5px; z-index: 10;"
                        onclick="photoGallery_${this.safeContainerId}.deletePhoto('${photo.filename}')"
                        title="Delete photo">
                    <i class="bi bi-trash" style="font-size: 12px;"></i>
                </button>
                ` : ''}

                <div class="photo-info position-absolute bottom-0 start-0 end-0 bg-dark bg-opacity-75 text-white p-2 rounded-bottom">
                    <small class="d-block text-truncate">${photo.original_filename || photo.filename}</small>
                    <small class="opacity-75">${this.formatFileSize(photo.file_size)}</small>
                </div>
            </div>
        `;

        return colDiv;
    }

    openLightbox(index) {
        if (index < 0 || index >= this.photos.length) return;

        const photo = this.photos[index];

        // Create lightbox modal
        const lightboxModal = document.createElement('div');
        lightboxModal.className = 'modal fade';
        lightboxModal.id = `lightbox_${this.containerId}_${index}`;
        lightboxModal.innerHTML = `
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${photo.original_filename || photo.filename}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="${photo.url}" class="img-fluid" alt="Full size photo">
                        <div class="mt-3">
                            <small class="text-muted">
                                Size: ${this.formatFileSize(photo.file_size)} |
                                Uploaded: ${photo.upload_date ? new Date(photo.upload_date).toLocaleString() : 'Unknown'}
                            </small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <a href="${photo.url}" class="btn btn-primary" download="${photo.original_filename || photo.filename}">
                            <i class="bi bi-download"></i> Download
                        </a>
                        ${this.options.allowDelete ? `
                        <button type="button" class="btn btn-danger"
                                onclick="photoGallery_${this.safeContainerId}.deletePhoto('${photo.filename}'); bootstrap.Modal.getInstance(this.closest('.modal')).hide();">
                            <i class="bi bi-trash"></i> Delete
                        </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(lightboxModal);

        // Show modal
        const modal = new bootstrap.Modal(lightboxModal);
        modal.show();

        // Clean up modal when hidden
        lightboxModal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(lightboxModal);
        });
    }

    async deletePhoto(filename) {
        if (!confirm('Are you sure you want to delete this photo?')) {
            return;
        }

        try {
            const response = await fetch(`/photos/delete/${this.options.category}/${filename}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (result.success) {
                // Remove photo from array
                this.photos = this.photos.filter(photo => photo.filename !== filename);

                // Re-render gallery
                this.renderPhotos();

                // Show success message
                this.showSuccess('Photo deleted successfully');

                if (this.options.onDelete) {
                    this.options.onDelete(filename, result);
                }
            } else {
                throw new Error(result.message || 'Delete failed');
            }

        } catch (error) {
            this.showError(`Failed to delete photo: ${error.message}`);

            if (this.options.onError) {
                this.options.onError(error);
            }
        }
    }

    addPhoto(photo) {
        this.photos.push(photo);
        this.renderPhotos();
    }

    addPhotos(photos) {
        this.photos.push(...photos);
        this.renderPhotos();
    }

    removePhoto(filename) {
        this.photos = this.photos.filter(photo => photo.filename !== filename);
        this.renderPhotos();
    }

    refresh() {
        this.loadPhotos();
    }

    showLoading(show) {
        if (show) {
            this.loadingContainer.classList.remove('d-none');
            this.gridContainer.classList.add('d-none');
            this.emptyContainer.classList.add('d-none');
        } else {
            this.loadingContainer.classList.add('d-none');
            this.gridContainer.classList.remove('d-none');
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        this.container.appendChild(errorDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                const bsAlert = new bootstrap.Alert(errorDiv);
                bsAlert.close();
            }
        }, 5000);
    }

    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-dismissible fade show mt-3';
        successDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        this.container.appendChild(successDiv);

        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                const bsAlert = new bootstrap.Alert(successDiv);
                bsAlert.close();
            }
        }, 3000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// CSS styles for photo gallery
const photoGalleryStyles = `
<style>
.photo-gallery .photo-item {
    transition: transform 0.2s ease;
}

.photo-gallery .photo-item:hover {
    transform: scale(1.05);
}

.photo-gallery .photo-thumbnail {
    transition: opacity 0.2s ease;
}

.photo-gallery .photo-thumbnail:hover {
    opacity: 0.8;
}

.photo-gallery .photo-info {
    transition: opacity 0.2s ease;
    opacity: 0;
}

.photo-gallery .photo-item:hover .photo-info {
    opacity: 1;
}

.photo-gallery .gallery-grid {
    min-height: 200px;
}
</style>
`;

// Inject styles
if (!document.querySelector('#photo-gallery-styles')) {
    const styleElement = document.createElement('div');
    styleElement.id = 'photo-gallery-styles';
    styleElement.innerHTML = photoGalleryStyles;
    document.head.appendChild(styleElement);
}

// Global function to initialize photo gallery
function initPhotoGallery(containerId, options = {}) {
    return new PhotoGallery(containerId, options);
}