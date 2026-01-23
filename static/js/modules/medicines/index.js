/**
 * Medicines module specific functionality
 */

import { loadPreviewFromUrl, showPreviewModal } from '../modals.js';
import { exportTableToCSV } from '../tables.js';
import { initBulkActions } from '../bulk-actions.js';
import { showAlert } from '../../utils/helpers.js';

let currentMedicineId = null;

/**
 * Initialize medicines index page
 */
export function initMedicinesIndex() {
    initTableFilters();
    initBulkActions('medicinesTable', 'medicines', '/medicines/bulk-delete');
}

/**
 * Initialize table filters for medicines
 */
function initTableFilters() {
    const supplierFilter = document.getElementById('supplierFilter');
    const stockFilter = document.getElementById('stockFilter');
    const searchInput = document.getElementById('searchInput');

    if (!supplierFilter || !stockFilter || !searchInput) {
        console.warn('Filter elements not found');
        return;
    }

    function filterTable() {
        const table = document.getElementById('medicinesTable');
        const tbody = table.getElementsByTagName('tbody')[0];
        const rows = tbody.getElementsByTagName('tr');

        const supplierValue = supplierFilter.value;
        const stockValue = stockFilter.value;
        const searchValue = searchInput.value.toLowerCase();

        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName('td');

            if (cells.length === 0) continue;

            let showRow = true;

            // Search filter
            if (searchValue) {
                const medicineName = cells[1].textContent.toLowerCase();
                const supplier = cells[2].textContent.toLowerCase();
                const form = cells[3].textContent.toLowerCase();
                const notes = cells[7].textContent.toLowerCase();

                if (!medicineName.includes(searchValue) &&
                    !supplier.includes(searchValue) &&
                    !form.includes(searchValue) &&
                    !notes.includes(searchValue)) {
                    showRow = false;
                }
            }

            // Supplier filter
            if (showRow && supplierValue !== '' && supplierValue !== 'All Suppliers') {
                const supplierIdFromRow = row.getAttribute('data-supplier-id');
                if (supplierIdFromRow !== supplierValue) {
                    showRow = false;
                }
            }

            // Stock level filter
            if (showRow && stockValue !== '' && stockValue !== 'All Stock Levels') {
                const statusCell = cells[6];
                const statusText = statusCell.textContent.trim();

                if ((stockValue === 'low' && !statusText.includes('Low Stock')) ||
                    (stockValue === 'medium' && !statusText.includes('Medium Stock')) ||
                    (stockValue === 'good' && !statusText.includes('Good Stock'))) {
                    showRow = false;
                }
            }

            row.style.display = showRow ? '' : 'none';
        }
    }

    // Add event listeners
    supplierFilter.addEventListener('change', filterTable);
    stockFilter.addEventListener('change', filterTable);
    searchInput.addEventListener('input', filterTable);
}

/**
 * Show medicine preview modal
 * @param {string} medicineId - Medicine ID
 * @param {string} medicineName - Medicine name
 */
export async function showMedicinePreview(medicineId, medicineName) {
    currentMedicineId = medicineId;
    const modal = new bootstrap.Modal(document.getElementById('medicinePreviewModal'));
    const content = document.getElementById('medicinePreviewContent');

    // Reset content
    content.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading medicine details...</p>
        </div>
    `;

    modal.show();

    try {
        // Fetch medicine details and photos
        const [medicineResponse, photosResponse] = await Promise.all([
            fetch(`/medicines/api/${medicineId}`),
            fetch(`/photos/list/medicines?entity_id=${medicineId}`)
        ]);

        if (!medicineResponse.ok) {
            throw new Error('Failed to load medicine details');
        }

        const medicineData = await medicineResponse.json();
        const photosData = photosResponse.ok ? await photosResponse.json() : { photos: [] };

        // Render medicine details
        renderMedicinePreview(medicineData, photosData.photos || []);

    } catch (error) {
        content.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                Error loading medicine details: ${error.message}
            </div>
        `;
    }
}

/**
 * Render medicine preview content
 * @param {Object} medicine - Medicine data
 * @param {Array} photos - Array of photos
 */
function renderMedicinePreview(medicine, photos) {
    const content = document.getElementById('medicinePreviewContent');

    content.innerHTML = `
        <div class="row">
            <!-- Medicine Photos Column -->
            <div class="col-md-5">
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="bi bi-images"></i> Photos</h6>
                    </div>
                    <div class="card-body">
                        ${photos.length > 0 ? `
                            <div class="row">
                                ${photos.slice(0, 4).map(photo => `
                                    <div class="col-6 mb-2">
                                        <img src="${photo.thumbnail_url || photo.url}"
                                             class="img-fluid rounded shadow-sm preview-photo"
                                             style="width: 100%; height: 80px; object-fit: cover; cursor: pointer;"
                                             onclick="openPhotoLightbox('${photo.url}', '${photo.original_filename}')"
                                             alt="Medicine photo">
                                    </div>
                                `).join('')}
                            </div>
                            ${photos.length > 4 ? `
                                <div class="text-center mt-2">
                                    <small class="text-muted">+${photos.length - 4} more photos</small>
                                </div>
                            ` : ''}
                        ` : `
                            <div class="text-center text-muted py-3">
                                <i class="bi bi-image fs-1 opacity-50"></i>
                                <p class="mt-2">No photos uploaded</p>
                            </div>
                        `}
                    </div>
                </div>
            </div>

            <!-- Medicine Details Column -->
            <div class="col-md-7">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="bi bi-info-circle"></i> Medicine Information</h6>
                    </div>
                    <div class="card-body">
                        <div class="row mb-2">
                            <div class="col-4"><strong>ID:</strong></div>
                            <div class="col-8">${medicine.id}</div>
                        </div>
                        <div class="row mb-2">
                            <div class="col-4"><strong>Name:</strong></div>
                            <div class="col-8"><h6 class="text-primary">${medicine.name}</h6></div>
                        </div>
                        <div class="row mb-2">
                            <div class="col-4"><strong>Supplier:</strong></div>
                            <div class="col-8">${medicine.supplier_name || 'N/A'}</div>
                        </div>
                        <div class="row mb-2">
                            <div class="col-4"><strong>Form/Dosage:</strong></div>
                            <div class="col-8">${medicine.form_dosage || 'N/A'}</div>
                        </div>
                        <div class="row mb-2">
                            <div class="col-4"><strong>Current Stock:</strong></div>
                            <div class="col-8">
                                <span class="badge ${medicine.stock_status === 'low' ? 'bg-danger' : medicine.stock_status === 'medium' ? 'bg-warning text-dark' : 'bg-success'}">
                                    ${medicine.current_stock || 0} units
                                </span>
                            </div>
                        </div>
                        <div class="row mb-2">
                            <div class="col-4"><strong>Low Stock Alert:</strong></div>
                            <div class="col-8">${medicine.low_stock_limit} units</div>
                        </div>
                        ${medicine.expiry_date ? `
                            <div class="row mb-2">
                                <div class="col-4"><strong>Expiry Date:</strong></div>
                                <div class="col-8">${new Date(medicine.expiry_date).toLocaleDateString()}</div>
                            </div>
                        ` : ''}
                        ${medicine.batch_number ? `
                            <div class="row mb-2">
                                <div class="col-4"><strong>Batch Number:</strong></div>
                                <div class="col-8"><code>${medicine.batch_number}</code></div>
                            </div>
                        ` : ''}
                        ${medicine.barcode_number ? `
                            <div class="row mb-2">
                                <div class="col-4"><strong>Barcode:</strong></div>
                                <div class="col-8"><code>${medicine.barcode_number}</code></div>
                            </div>
                        ` : ''}
                        ${medicine.notes ? `
                            <div class="row mb-2">
                                <div class="col-4"><strong>Notes:</strong></div>
                                <div class="col-8">${medicine.notes}</div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Open photo lightbox
 * @param {string} photoUrl - Photo URL
 * @param {string} filename - Photo filename
 */
function openPhotoLightbox(photoUrl, filename) {
    const lightboxModal = document.createElement('div');
    lightboxModal.className = 'modal fade';
    lightboxModal.innerHTML = `
        <div class="modal-dialog modal-lg modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${filename}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body text-center">
                    <img src="${photoUrl}" class="img-fluid" alt="Medicine photo">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <a href="${photoUrl}" class="btn btn-primary" download="${filename}">
                        <i class="bi bi-download"></i> Download
                    </a>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(lightboxModal);
    const modal = new bootstrap.Modal(lightboxModal);
    modal.show();

    // Clean up modal when hidden
    lightboxModal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(lightboxModal);
    });
}

/**
 * Edit current medicine
 */
export function editCurrentMedicine() {
    if (currentMedicineId) {
        window.location.href = `/medicines/edit/${currentMedicineId}`;
    }
}

// Auto-initialize on page load if on medicines index page
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        if (document.getElementById('medicinesTable')) {
            initMedicinesIndex();
        }
    });
} else {
    if (document.getElementById('medicinesTable')) {
        initMedicinesIndex();
    }
}
