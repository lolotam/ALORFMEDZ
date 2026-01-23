/**
 * Modal utilities and helpers
 */

import { showAlert } from '../utils/helpers.js';

/**
 * Initialize confirm delete modal
 * @param {string} modalId - ID of the confirm delete modal
 * @param {string} deleteUrl - URL to call when confirmed
 * @param {function} onSuccess - Callback after successful delete
 */
export function initConfirmDelete(modalId = 'confirmDeleteModal', deleteUrl = '', onSuccess = null) {
    const modal = document.getElementById(modalId);
    const confirmBtn = document.getElementById('confirmDeleteBtn');

    if (confirmBtn) {
        confirmBtn.addEventListener('click', async function() {
            if (!deleteUrl) {
                console.error('Delete URL not provided');
                return;
            }

            // Show loading state
            const originalText = this.innerHTML;
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Deleting...';

            try {
                const response = await fetch(deleteUrl, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const result = await response.json();

                if (result.success) {
                    // Hide modal
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) {
                        bsModal.hide();
                    }

                    // Show success message
                    showAlert('success', result.message || 'Item deleted successfully.');

                    // Call success callback
                    if (onSuccess) {
                        onSuccess(result);
                    } else {
                        // Default: reload page
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }
                } else {
                    throw new Error(result.message || 'Delete failed');
                }
            } catch (error) {
                console.error('Delete error:', error);
                showAlert('danger', 'Error: ' + error.message);
                this.disabled = false;
                this.innerHTML = originalText;
            }
        });
    }
}

/**
 * Show confirm delete modal
 * @param {string} message - Custom message to display
 * @param {string} deleteUrl - URL to call when confirmed
 * @param {function} onSuccess - Callback after successful delete
 */
export function showConfirmDelete(message = 'Are you sure you want to delete this item?', deleteUrl = '', onSuccess = null) {
    const messageEl = document.getElementById('confirmDeleteMessage');
    if (messageEl) {
        messageEl.textContent = message;
    }

    initConfirmDelete('confirmDeleteModal', deleteUrl, onSuccess);

    const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    modal.show();
}

/**
 * Initialize import modal functionality
 */
export function initImportModal() {
    const importForm = document.getElementById('importForm');
    const importBtn = document.getElementById('importBtn');

    if (importForm && importBtn) {
        importForm.addEventListener('submit', function(e) {
            // Show loading state
            importBtn.disabled = true;
            importBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Importing...';
        });
    }
}

/**
 * Show preview modal with content
 * @param {string} title - Modal title
 * @param {string} content - HTML content to display
 * @param {function} onLoad - Callback after modal is shown
 */
export function showPreviewModal(title, content, onLoad = null) {
    const modal = document.getElementById('previewModal');
    const titleEl = document.getElementById('previewModalTitle');
    const contentEl = document.getElementById('previewModalContent');

    if (titleEl) {
        titleEl.innerHTML = `<i class="bi bi-eye"></i> ${title}`;
    }

    if (contentEl) {
        contentEl.innerHTML = content;
    }

    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();

    if (onLoad) {
        onLoad();
    }
}

/**
 * Load preview content from URL
 * @param {string} title - Modal title
 * @param {string} url - URL to fetch content from
 * @param {function} onLoad - Callback after load
 */
export async function loadPreviewFromUrl(title, url, onLoad = null) {
    const modal = document.getElementById('previewModal');
    const titleEl = document.getElementById('previewModalTitle');
    const contentEl = document.getElementById('previewModalContent');

    if (titleEl) {
        titleEl.innerHTML = `<i class="bi bi-eye"></i> ${title}`;
    }

    if (contentEl) {
        contentEl.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading...</p>
            </div>
        `;
    }

    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            if (contentEl) {
                contentEl.innerHTML = data.content || 'No content available.';
            }
            if (onLoad) {
                onLoad(data);
            }
        } else {
            throw new Error(data.message || 'Failed to load preview');
        }
    } catch (error) {
        console.error('Preview error:', error);
        if (contentEl) {
            contentEl.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    Error loading preview: ${error.message}
                </div>
            `;
        }
    }
}

// Auto-initialize modals
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        initImportModal();
    });
} else {
    initImportModal();
}
