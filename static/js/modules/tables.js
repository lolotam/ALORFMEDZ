/**
 * Table functionality: search, filter, export
 */

import { showAlert } from '../utils/helpers.js';
import { formatCurrency } from '../utils/formatters.js';

/**
 * Initialize table search and filter functionality
 * @param {string} inputId - ID of search input
 * @param {string} tableId - ID of table element
 */
export function initTableSearch(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);

    if (!input || !table) {
        console.warn('Table elements not found:', inputId, tableId);
        return;
    }

    input.addEventListener('keyup', function() {
        filterTableRows(input, table);
    });
}

/**
 * Filter table rows based on search input
 * @param {HTMLInputElement} input - Search input element
 * @param {HTMLTableElement} table - Table element
 */
function filterTableRows(input, table) {
    const filter = input.value.toLowerCase();
    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
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
}

/**
 * Advanced table filtering with multiple criteria
 * @param {Object} filters - Filter criteria
 * @param {string} tableId - ID of table element
 */
export function filterTable(filters, tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        let showRow = true;

        // Apply each filter
        for (const [filterKey, filterValue] of Object.entries(filters)) {
            if (!filterValue) continue;

            const cell = row.querySelector(`[data-${filterKey}]`);
            if (cell) {
                const cellValue = cell.getAttribute(`data-${filterKey}`).toLowerCase();
                if (!cellValue.includes(filterValue.toLowerCase())) {
                    showRow = false;
                    break;
                }
            }
        }

        row.style.display = showRow ? '' : 'none';
    }
}

/**
 * Export table to CSV
 * @param {string} tableId - ID of table element
 * @param {string} filename - Filename for export
 */
export function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) {
        console.error('Table not found:', tableId);
        return;
    }

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

    showAlert('success', 'Table exported successfully!');
}

/**
 * Export purchases with detailed medicine breakdown
 */
export function exportPurchasesToCSV() {
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

    downloadCSV(csv, 'purchases_detailed.csv');
}

/**
 * Export consumption with detailed medicine breakdown
 */
export function exportConsumptionToCSV() {
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

    downloadCSV(csv, 'consumption_detailed.csv');
}

/**
 * Export consumption report with filtered data
 */
export function exportConsumptionReportToCSV() {
    const table = document.getElementById('consumptionReportTable');
    if (!table) return;

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

    downloadCSV(csv, 'consumption_report_filtered.csv');
}

/**
 * Download CSV file
 * @param {Array} csvData - CSV data array
 * @param {string} filename - Filename to download
 */
function downloadCSV(csvData, filename) {
    const csvContent = csvData.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);

    showAlert('success', 'Data exported successfully!');
}
