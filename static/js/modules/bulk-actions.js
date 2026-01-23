/**
 * Bulk actions functionality (select all, bulk delete, etc.)
 */

import { showAlert } from '../utils/helpers.js';

/**
 * Initialize bulk actions for a table
 * @param {string} tableId - ID of the table
 * @param {string} moduleName - Name of the module (for validation)
 * @param {string} deleteUrl - URL for bulk delete endpoint
 */
export function initBulkActions(tableId, moduleName, deleteUrl) {
    const table = document.getElementById(tableId);
    if (!table) {
        console.warn('Table not found:', tableId);
        return;
    }

    // Add checkboxes to table
    addBulkDeleteCheckboxes(table);

    // Add bulk delete controls
    addBulkDeleteControls(table, moduleName, deleteUrl);

    // Initialize event handlers
    initializeBulkDeleteHandlers(table, moduleName, deleteUrl);
}

/**
 * Add checkboxes to table rows
 * @param {HTMLTableElement} table - Table element
 */
function addBulkDeleteCheckboxes(table) {
    const thead = table.querySelector('thead tr');
    const tbody = table.querySelector('tbody');

    if (!thead || !tbody) return;

    // Add checkbox header
    const checkboxHeader = document.createElement('th');
    checkboxHeader.innerHTML = `
        <input type="checkbox" class="form-check-input" id="selectAll" title="Select All">
    `;
    thead.insertBefore(checkboxHeader, thead.firstChild);

    // Add checkboxes to each row
    const rows = tbody.querySelectorAll('tr');
    rows.forEach(row => {
        const checkboxCell = document.createElement('td');
        const itemId = row.getAttribute('data-id') || row.cells[0].textContent.trim();

        // Disable checkbox for main department or main store (ID '01')
        const isMainItem = itemId === '01';
        const disabledAttr = isMainItem ? 'disabled title="Cannot delete main item"' : '';

        checkboxCell.innerHTML = `
            <input type="checkbox" class="form-check-input bulk-select" value="${itemId}" ${disabledAttr}>
        `;
        row.insertBefore(checkboxCell, row.firstChild);
        row.setAttribute('data-id', itemId);
    });
}

/**
 * Add bulk delete controls above table
 * @param {HTMLTableElement} table - Table element
 * @param {string} moduleName - Module name
 * @param {string} deleteUrl - Delete URL
 */
function addBulkDeleteControls(table, moduleName, deleteUrl) {
    const controlDiv = document.createElement('div');
    controlDiv.className = 'd-flex justify-content-between align-items-center mb-3';
    controlDiv.id = 'bulkDeleteControls';
    controlDiv.style.display = 'none';

    controlDiv.innerHTML = `
        <div>
            <span class="badge bg-info" id="selectedCount">0 selected</span>
        </div>
        <button class="btn btn-danger btn-sm" id="bulkDeleteBtn" onclick="performBulkDelete('${moduleName}', '${deleteUrl}')">
            <i class="bi bi-trash"></i> Delete Selected
        </button>
    `;

    table.parentNode.insertBefore(controlDiv, table);
}

/**
 * Initialize event handlers for bulk delete
 * @param {HTMLTableElement} table - Table element
 * @param {string} moduleName - Module name
 * @param {string} deleteUrl - Delete URL
 */
function initializeBulkDeleteHandlers(table, moduleName, deleteUrl) {
    // Select all checkbox
    const selectAllCheckbox = table.querySelector('#selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = table.querySelectorAll('.bulk-select');
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkDeleteControls(table);
        });
    }

    // Individual checkboxes
    table.addEventListener('change', function(e) {
        if (e.target.classList.contains('bulk-select')) {
            updateSelectAllCheckbox(table);
            updateBulkDeleteControls(table);
        }
    });
}

/**
 * Update select all checkbox state
 * @param {HTMLTableElement} table - Table element
 */
function updateSelectAllCheckbox(table) {
    const selectAll = table.querySelector('#selectAll');
    if (!selectAll) return;

    const checkboxes = table.querySelectorAll('.bulk-select');
    const checkedBoxes = table.querySelectorAll('.bulk-select:checked');

    if (checkboxes.length === 0) {
        selectAll.checked = false;
        selectAll.indeterminate = false;
    } else if (checkedBoxes.length === 0) {
        selectAll.checked = false;
        selectAll.indeterminate = false;
    } else if (checkedBoxes.length === checkboxes.length) {
        selectAll.checked = true;
        selectAll.indeterminate = false;
    } else {
        selectAll.checked = false;
        selectAll.indeterminate = true;
    }
}

/**
 * Update bulk delete controls visibility and count
 * @param {HTMLTableElement} table - Table element
 */
function updateBulkDeleteControls(table) {
    const controlDiv = document.getElementById('bulkDeleteControls');
    const selectedCount = document.getElementById('selectedCount');
    const checkedBoxes = table.querySelectorAll('.bulk-select:checked');

    if (controlDiv && selectedCount) {
        if (checkedBoxes.length > 0) {
            controlDiv.style.display = 'flex';
            selectedCount.textContent = `${checkedBoxes.length} selected`;
        } else {
            controlDiv.style.display = 'none';
        }
    }
}

/**
 * Perform bulk delete
 * @param {string} moduleName - Name of the module
 * @param {string} deleteUrl - URL for bulk delete
 */
export async function performBulkDelete(moduleName, deleteUrl) {
    const checkedBoxes = document.querySelectorAll('.bulk-select:checked');
    const selectedIds = Array.from(checkedBoxes).map(cb => cb.value);

    if (selectedIds.length === 0) {
        alert('Please select at least one item to delete.');
        return;
    }

    // Special validation for stores module
    if (moduleName === 'stores' && selectedIds.includes('01')) {
        alert('The Main Store cannot be deleted.');
        return;
    }

    // Special validation for departments module
    if (moduleName === 'departments' && selectedIds.includes('01')) {
        alert('The Main Department cannot be deleted.');
        return;
    }

    const confirmMessage = `Are you sure you want to delete ${selectedIds.length} ${moduleName}? This action cannot be undone.`;
    if (!confirm(confirmMessage)) {
        return;
    }

    try {
        // Show loading state
        const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
        const originalText = bulkDeleteBtn.innerHTML;
        bulkDeleteBtn.disabled = true;
        bulkDeleteBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Deleting...';

        const response = await fetch(deleteUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: selectedIds })
        });

        const result = await response.json();

        if (result.success) {
            // Remove deleted rows from DOM immediately for instant visual feedback
            selectedIds.forEach(id => {
                const row = document.querySelector(`tr[data-id="${id}"]`);
                if (row) {
                    row.remove();
                }
            });

            // Hide bulk delete controls
            const controlDiv = document.getElementById('bulkDeleteControls');
            if (controlDiv) {
                controlDiv.style.display = 'none';
            }

            // Uncheck select all checkbox
            const selectAllCheckbox = document.querySelector('#selectAll');
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = false;
            }

            // Show success message
            showAlert('success', result.message || `Successfully deleted ${selectedIds.length} ${moduleName}.`);

            // Reload page after delay to refresh data and ensure consistency
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showAlert('danger', result.message || 'Failed to delete selected items.');
            bulkDeleteBtn.disabled = false;
            bulkDeleteBtn.innerHTML = originalText;
        }
    } catch (error) {
        console.error('Error during bulk delete:', error);
        showAlert('danger', 'An error occurred while deleting items.');

        // Restore button
        const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
        bulkDeleteBtn.disabled = false;
        bulkDeleteBtn.innerHTML = '<i class="bi bi-trash"></i> Delete Selected';
    }
}
