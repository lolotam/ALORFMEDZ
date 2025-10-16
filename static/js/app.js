// Hospital Pharmacy Management System - JavaScript

// Sidebar functionality
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    // Toggle sidebar on mobile
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            sidebarOverlay.classList.toggle('show');
        });
    }

    // Close sidebar when clicking overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
        });
    }

    // Close sidebar when clicking a link on mobile
    const sidebarLinks = document.querySelectorAll('.sidebar-nav-link');
    sidebarLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 992) {
                sidebar.classList.remove('show');
                sidebarOverlay.classList.remove('show');
            }
        });
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 992) {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
        }
    });
});

// Theme toggle functionality
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    html.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    // Update theme text
    const themeText = document.getElementById('theme-text');
    if (themeText) {
        themeText.textContent = newTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
    }
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);

    const themeText = document.getElementById('theme-text');
    if (themeText) {
        themeText.textContent = savedTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
    }
});

// Confirm delete actions
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Add medicine row in forms
function addMedicineRow(containerId) {
    const container = document.getElementById(containerId);
    const rowCount = container.children.length;
    
    const newRow = document.createElement('div');
    newRow.className = 'row mb-2 medicine-row';
    newRow.innerHTML = `
        <div class="col-md-6">
            <select class="form-select" name="medicine_id[]" required>
                <option value="">Select Medicine</option>
                ${getMedicineOptions()}
            </select>
        </div>
        <div class="col-md-4">
            <input type="number" class="form-control" name="quantity[]" placeholder="Quantity" min="1" required>
        </div>
        <div class="col-md-2">
            <button type="button" class="btn btn-danger btn-sm" onclick="removeMedicineRow(this)">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    
    container.appendChild(newRow);
}

// Remove medicine row
function removeMedicineRow(button) {
    const row = button.closest('.medicine-row');
    row.remove();
}

// Get medicine options (to be populated by backend)
function getMedicineOptions() {
    // This will be populated by the backend template
    return '';
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString();
}

// Show loading spinner
function showLoading(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Loading...';
    }
}

// Hide loading spinner
function hideLoading(buttonId, originalText) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Table search functionality
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    
    input.addEventListener('keyup', function() {
        const filter = input.value.toLowerCase();
        
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let found = false;
            
            for (let j = 0; j < cells.length; j++) {
                const cell = cells[j];
                if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
            
            row.style.display = found ? '' : 'none';
        }
    });
}

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tr');
    const csv = [];

    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];

        for (let j = 0; j < cols.length - 1; j++) { // Exclude last column (actions)
            const col = cols[j];
            let cellValue;

            // Check if cell has data-export-value attribute
            if (col.hasAttribute('data-export-value')) {
                cellValue = col.getAttribute('data-export-value');
            } else {
                cellValue = col.textContent.trim();
            }

            csvRow.push('"' + cellValue.replace(/"/g, '""') + '"');
        }

        csv.push(csvRow.join(','));
    }

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename + '.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Export purchases with detailed medicine breakdown
function exportPurchasesToCSV() {
    // Get purchase data from the page
    const purchaseRows = document.querySelectorAll('#purchasesTable tbody tr');
    const csv = [];

    // Headers for detailed export
    const headers = ['Purchase ID', 'Date', 'Supplier', 'Invoice Number', 'Medicine Name', 'Medicine Form/Dosage', 'Quantity', 'Status', 'Notes'];
    csv.push(headers.join(','));

    purchaseRows.forEach(row => {
        const purchaseId = row.cells[0].textContent.trim();
        const date = row.cells[1].textContent.trim();
        const supplier = row.cells[2].textContent.trim();
        const invoiceNumber = row.cells[3].textContent.trim();
        const status = row.cells[5].textContent.trim();
        const notes = row.cells[6].textContent.trim();

        // Get medicine details from the modal
        const modalId = `itemsModal${purchaseId}`;
        const modal = document.getElementById(modalId);

        if (modal) {
            const medicineRows = modal.querySelectorAll('tbody tr');
            let isFirstMedicine = true;

            medicineRows.forEach(medicineRow => {
                const medicineName = medicineRow.cells[0].textContent.trim();
                const medicineForm = medicineRow.cells[1].textContent.trim();
                const quantity = medicineRow.cells[2].textContent.trim();

                const csvRow = [];

                if (isFirstMedicine) {
                    // First row includes all purchase details
                    csvRow.push(`"${purchaseId}"`);
                    csvRow.push(`"${date}"`);
                    csvRow.push(`"${supplier}"`);
                    csvRow.push(`"${invoiceNumber}"`);
                    csvRow.push(`"${medicineName}"`);
                    csvRow.push(`"${medicineForm}"`);
                    csvRow.push(`"${quantity}"`);
                    csvRow.push(`"${status}"`);
                    csvRow.push(`"${notes}"`);
                    isFirstMedicine = false;
                } else {
                    // Subsequent rows only have medicine details
                    csvRow.push('""'); // Empty Purchase ID
                    csvRow.push('""'); // Empty Date
                    csvRow.push('""'); // Empty Supplier
                    csvRow.push('""'); // Empty Invoice Number
                    csvRow.push(`"${medicineName}"`);
                    csvRow.push(`"${medicineForm}"`);
                    csvRow.push(`"${quantity}"`);
                    csvRow.push('""'); // Empty Status
                    csvRow.push('""'); // Empty Notes
                }

                csv.push(csvRow.join(','));
            });
        }
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'purchases_detailed.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Export consumption with detailed medicine breakdown
function exportConsumptionToCSV() {
    // Get consumption data from the page
    const consumptionRows = document.querySelectorAll('#consumptionTable tbody tr');
    const csv = [];

    // Headers for detailed export
    const headers = ['Consumption ID', 'Date', 'Patient Name', 'Prescribed By', 'Department', 'Medicine Name', 'Medicine Form/Dosage', 'Quantity', 'Notes'];
    csv.push(headers.join(','));

    consumptionRows.forEach(row => {
        const consumptionId = row.cells[0].textContent.trim();
        const date = row.cells[1].textContent.trim();
        const patientName = row.cells[2].textContent.trim();
        const prescribedBy = row.cells[3].textContent.trim();

        // Check if admin view (has department column)
        const isAdmin = row.cells.length > 8; // Admin has more columns
        const department = isAdmin ? row.cells[4].textContent.trim() : '';
        const notesIndex = isAdmin ? 7 : 6;
        const notes = row.cells[notesIndex].textContent.trim();

        // Get medicine details from the modal
        const modalId = `itemsModal${consumptionId}`;
        const modal = document.getElementById(modalId);

        if (modal) {
            const medicineRows = modal.querySelectorAll('tbody tr');
            let isFirstMedicine = true;

            medicineRows.forEach(medicineRow => {
                const medicineName = medicineRow.cells[0].textContent.trim();
                const medicineForm = medicineRow.cells[1].textContent.trim();
                const quantity = medicineRow.cells[2].textContent.trim();

                const csvRow = [];

                if (isFirstMedicine) {
                    // First row includes all consumption details
                    csvRow.push(`"${consumptionId}"`);
                    csvRow.push(`"${date}"`);
                    csvRow.push(`"${patientName}"`);
                    csvRow.push(`"${prescribedBy}"`);
                    csvRow.push(`"${department}"`);
                    csvRow.push(`"${medicineName}"`);
                    csvRow.push(`"${medicineForm}"`);
                    csvRow.push(`"${quantity}"`);
                    csvRow.push(`"${notes}"`);
                    isFirstMedicine = false;
                } else {
                    // Subsequent rows only have medicine details
                    csvRow.push('""'); // Empty Consumption ID
                    csvRow.push('""'); // Empty Date
                    csvRow.push('""'); // Empty Patient Name
                    csvRow.push('""'); // Empty Prescribed By
                    csvRow.push('""'); // Empty Department
                    csvRow.push(`"${medicineName}"`);
                    csvRow.push(`"${medicineForm}"`);
                    csvRow.push(`"${quantity}"`);
                    csvRow.push('""'); // Empty Notes
                }

                csv.push(csvRow.join(','));
            });
        }
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'consumption_detailed.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Export consumption report with detailed medicine breakdown
function exportConsumptionReportToCSV() {
    // Export only visible/filtered rows from the consumption report table
    const table = document.getElementById('consumptionReportTable');
    const rows = table.querySelectorAll('tr:not([style*="display: none"])'); // Only visible rows
    const csv = [];

    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];

        for (let j = 0; j < cols.length - 1; j++) { // Exclude last column (actions)
            const col = cols[j];
            let cellValue;

            // Check if cell has data-export-value attribute
            if (col.hasAttribute('data-export-value')) {
                cellValue = col.getAttribute('data-export-value');
            } else {
                cellValue = col.textContent.trim();
            }

            csvRow.push('"' + cellValue.replace(/"/g, '""') + '"');
        }

        csv.push(csvRow.join(','));
    }

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'consumption_report_filtered.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Print functionality
function printPage() {
    window.print();
}

// ========== BULK DELETE FUNCTIONALITY ==========

// Initialize bulk delete functionality
function initBulkDelete(tableId, moduleName, deleteUrl) {
    const table = document.getElementById(tableId);
    if (!table) return;

    // Add checkboxes to table
    addBulkDeleteCheckboxes(table);

    // Add bulk delete controls
    addBulkDeleteControls(table, moduleName, deleteUrl);

    // Initialize event handlers
    initializeBulkDeleteHandlers(table, moduleName);
}

// Add checkboxes to table rows
function addBulkDeleteCheckboxes(table) {
    const thead = table.querySelector('thead tr');
    const tbody = table.querySelector('tbody');

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

// Add bulk delete controls above table
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

// Initialize event handlers for bulk delete
function initializeBulkDeleteHandlers(table, moduleName) {
    // Select all checkbox
    const selectAllCheckbox = table.querySelector('#selectAll');
    selectAllCheckbox.addEventListener('change', function() {
        const checkboxes = table.querySelectorAll('.bulk-select');
        checkboxes.forEach(checkbox => {
            checkbox.checked = this.checked;
        });
        updateBulkDeleteControls(table);
    });

    // Individual checkboxes
    table.addEventListener('change', function(e) {
        if (e.target.classList.contains('bulk-select')) {
            updateSelectAllCheckbox(table);
            updateBulkDeleteControls(table);
        }
    });
}

// Update select all checkbox state
function updateSelectAllCheckbox(table) {
    const selectAll = table.querySelector('#selectAll');
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

// Update bulk delete controls visibility and count
function updateBulkDeleteControls(table) {
    const controlDiv = document.getElementById('bulkDeleteControls');
    const selectedCount = document.getElementById('selectedCount');
    const checkedBoxes = table.querySelectorAll('.bulk-select:checked');

    if (checkedBoxes.length > 0) {
        controlDiv.style.display = 'flex';
        selectedCount.textContent = `${checkedBoxes.length} selected`;
    } else {
        controlDiv.style.display = 'none';
    }
}

// Perform bulk delete
async function performBulkDelete(moduleName, deleteUrl) {
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

// Show alert message
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Find container or create one
    let alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alertContainer';
        alertContainer.className = 'container mt-3';
        const mainContent = document.querySelector('.container, main');
        mainContent.insertBefore(alertContainer, mainContent.firstChild);
    }

    alertContainer.appendChild(alertDiv);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}
