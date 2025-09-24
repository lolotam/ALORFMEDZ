/**
 * Photo Upload Component
 * Handles drag-and-drop photo uploads with preview and validation
 */

class PhotoUpload {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            category: options.category || 'medicines',
            entityId: options.entityId || null,
            maxFiles: options.maxFiles || 1,
            maxFileSize: options.maxFileSize || 16 * 1024 * 1024, // 16MB
            allowedTypes: options.allowedTypes || ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'],
            showPreview: options.showPreview !== false,
            showProgress: options.showProgress !== false,
            onSuccess: options.onSuccess || null,
            onError: options.onError || null,
            onProgress: options.onProgress || null,
            endpoint: options.endpoint || '/photos/upload'
        };

        this.files = [];
        this.uploading = false;

        this.init();
    }

    init() {
        if (!this.container) {
            console.error('Photo upload container not found');
            return;
        }

        this.createUploadArea();
        this.setupEventListeners();
    }

    createUploadArea() {
        this.container.innerHTML = `
            <div class="photo-upload-area">
                <div class="upload-dropzone" id="${this.container.id}_dropzone">
                    <div class="upload-content">
                        <i class="bi bi-cloud-upload fs-1 text-muted"></i>
                        <h5 class="mt-2">Upload Photos</h5>
                        <p class="text-muted">
                            Drag and drop photos here or
                            <span class="text-primary" style="cursor: pointer;" id="${this.container.id}_browse">browse files</span>
                        </p>
                        <small class="text-muted">
                            Max ${this.options.maxFiles} file(s), up to ${this.formatFileSize(this.options.maxFileSize)} each
                        </small>
                    </div>
                </div>
                <input type="file" id="${this.container.id}_input" class="d-none" multiple
                       accept="${this.options.allowedTypes.join(',')}"
                       ${this.options.maxFiles === 1 ? '' : 'multiple'}>
                <div class="upload-progress mt-3 d-none" id="${this.container.id}_progress">
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                    </div>
                    <small class="text-muted mt-1 d-block" id="${this.container.id}_progress_text">Uploading...</small>
                </div>
                <div class="upload-preview mt-3" id="${this.container.id}_preview"></div>
                <div class="upload-errors mt-3" id="${this.container.id}_errors"></div>
            </div>
        `;

        this.dropzone = this.container.querySelector('.upload-dropzone');
        this.fileInput = document.getElementById(`${this.container.id}_input`);
        this.browseButton = document.getElementById(`${this.container.id}_browse`);
        this.progressContainer = document.getElementById(`${this.container.id}_progress`);
        this.progressBar = this.progressContainer.querySelector('.progress-bar');
        this.progressText = document.getElementById(`${this.container.id}_progress_text`);
        this.previewContainer = document.getElementById(`${this.container.id}_preview`);
        this.errorsContainer = document.getElementById(`${this.container.id}_errors`);
    }

    setupEventListeners() {
        // Browse button click
        this.browseButton.addEventListener('click', () => {
            this.fileInput.click();
        });

        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFiles(Array.from(e.target.files));
        });

        // Drag and drop events
        this.dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.dropzone.classList.add('drag-over');
        });

        this.dropzone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.dropzone.classList.remove('drag-over');
        });

        this.dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropzone.classList.remove('drag-over');
            const files = Array.from(e.dataTransfer.files);
            this.handleFiles(files);
        });
    }

    handleFiles(files) {
        this.clearErrors();

        // Validate file count
        if (files.length > this.options.maxFiles) {
            this.showError(`Maximum ${this.options.maxFiles} file(s) allowed`);
            return;
        }

        // Validate each file
        const validFiles = [];
        for (const file of files) {
            if (this.validateFile(file)) {
                validFiles.push(file);
            }
        }

        if (validFiles.length === 0) {
            return;
        }

        this.files = validFiles;

        if (this.options.showPreview) {
            this.showPreview(validFiles);
        }

        // Auto-upload if single file mode
        if (this.options.maxFiles === 1 && validFiles.length === 1) {
            this.upload();
        }
    }

    validateFile(file) {
        // Check file type
        if (!this.options.allowedTypes.includes(file.type)) {
            this.showError(`Invalid file type: ${file.name}. Allowed types: ${this.options.allowedTypes.join(', ')}`);
            return false;
        }

        // Check file size
        if (file.size > this.options.maxFileSize) {
            this.showError(`File too large: ${file.name}. Maximum size: ${this.formatFileSize(this.options.maxFileSize)}`);
            return false;
        }

        return true;
    }

    showPreview(files) {
        this.previewContainer.innerHTML = '';

        files.forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const previewItem = document.createElement('div');
                previewItem.className = 'preview-item d-inline-block me-2 mb-2 position-relative';
                previewItem.innerHTML = `
                    <img src="${e.target.result}" class="preview-image border rounded"
                         style="width: 100px; height: 100px; object-fit: cover;">
                    <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0 rounded-circle"
                            style="width: 20px; height: 20px; margin: -5px;" onclick="this.parentElement.remove()">
                        <i class="bi bi-x" style="font-size: 12px;"></i>
                    </button>
                    <div class="mt-1">
                        <small class="text-muted d-block">${file.name}</small>
                        <small class="text-muted">${this.formatFileSize(file.size)}</small>
                    </div>
                `;
                this.previewContainer.appendChild(previewItem);
            };
            reader.readAsDataURL(file);
        });

        // Add upload button for multiple files
        if (this.options.maxFiles > 1) {
            const uploadButton = document.createElement('div');
            uploadButton.className = 'mt-2';
            uploadButton.innerHTML = `
                <button type="button" class="btn btn-primary btn-sm" onclick="photoUpload_${this.container.id}.upload()">
                    <i class="bi bi-upload"></i> Upload ${files.length} Photo(s)
                </button>
            `;
            this.previewContainer.appendChild(uploadButton);
        }

        // Store reference for button onclick
        window[`photoUpload_${this.container.id}`] = this;
    }

    async upload() {
        if (this.uploading || this.files.length === 0) {
            return;
        }

        this.uploading = true;
        this.showProgress(true);
        this.clearErrors();

        try {
            const formData = new FormData();

            // Add files
            this.files.forEach(file => {
                formData.append('photo', file);
            });

            // Add entity ID if provided
            if (this.options.entityId) {
                formData.append('entity_id', this.options.entityId);
            }

            // Determine endpoint
            const endpoint = this.files.length > 1
                ? `${this.options.endpoint}/${this.options.category}/multiple`
                : `${this.options.endpoint}/${this.options.category}`;

            // Upload with progress tracking
            const response = await this.uploadWithProgress(endpoint, formData);
            const result = await response.json();

            if (result.success) {
                this.showProgress(false);
                this.showSuccess(`Uploaded ${this.files.length} photo(s) successfully`);

                if (this.options.onSuccess) {
                    this.options.onSuccess(result);
                }

                // Reset for next upload
                this.reset();
            } else {
                throw new Error(result.message || 'Upload failed');
            }

        } catch (error) {
            this.showProgress(false);
            this.showError(`Upload failed: ${error.message}`);

            if (this.options.onError) {
                this.options.onError(error);
            }
        } finally {
            this.uploading = false;
        }
    }

    uploadWithProgress(url, formData) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            xhr.upload.onprogress = (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    this.updateProgress(percentComplete);

                    if (this.options.onProgress) {
                        this.options.onProgress(percentComplete);
                    }
                }
            };

            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(xhr);
                } else {
                    reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
                }
            };

            xhr.onerror = () => reject(new Error('Network error'));
            xhr.onabort = () => reject(new Error('Upload aborted'));

            xhr.open('POST', url);
            xhr.send(formData);
        });
    }

    showProgress(show) {
        if (!this.options.showProgress) return;

        if (show) {
            this.progressContainer.classList.remove('d-none');
            this.updateProgress(0);
        } else {
            this.progressContainer.classList.add('d-none');
        }
    }

    updateProgress(percent) {
        if (!this.options.showProgress) return;

        this.progressBar.style.width = `${percent}%`;
        this.progressText.textContent = `Uploading... ${Math.round(percent)}%`;
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        this.errorsContainer.appendChild(errorDiv);
    }

    showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-dismissible fade show';
        successDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        this.errorsContainer.appendChild(successDiv);

        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(successDiv);
            bsAlert.close();
        }, 3000);
    }

    clearErrors() {
        this.errorsContainer.innerHTML = '';
    }

    reset() {
        this.files = [];
        this.fileInput.value = '';
        this.previewContainer.innerHTML = '';
        this.showProgress(false);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// CSS styles for photo upload
const photoUploadStyles = `
<style>
.photo-upload-area .upload-dropzone {
    border: 2px dashed #ccc;
    border-radius: 8px;
    padding: 40px 20px;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
}

.photo-upload-area .upload-dropzone:hover,
.photo-upload-area .upload-dropzone.drag-over {
    border-color: #007bff;
    background-color: #f8f9fa;
}

.photo-upload-area .preview-item {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 8px;
    background: white;
}

.photo-upload-area .preview-image {
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
`;

// Inject styles
if (!document.querySelector('#photo-upload-styles')) {
    const styleElement = document.createElement('div');
    styleElement.id = 'photo-upload-styles';
    styleElement.innerHTML = photoUploadStyles;
    document.head.appendChild(styleElement);
}

// Global function to initialize photo upload
function initPhotoUpload(containerId, options = {}) {
    return new PhotoUpload(containerId, options);
}