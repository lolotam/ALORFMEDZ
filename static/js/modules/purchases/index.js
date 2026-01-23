/**
 * Purchases Management Module
 * Handles purchases-specific functionality
 */

/**
 * Print a purchase
 * @param {string} purchaseId - ID of the purchase to print
 */
function printPurchase(purchaseId) {
    // TODO: Implement print functionality
    alert('Print purchase ID: ' + purchaseId);
}

/**
 * Filter table based on search and filter inputs
 */
function filterTable() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const supplierFilter = document.getElementById('supplierFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const purchaserFilter = document.getElementById('purchaserFilter').value;
    const dateFromFilter = document.getElementById('dateFromFilter').value;
    const dateToFilter = document.getElementById('dateToFilter').value;

    const table = document.getElementById('purchasesTable');
    const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');

    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const supplierID = row.getAttribute('data-supplier-id');
        const status = row.getAttribute('data-status');
        const purchaser = row.getAttribute('data-purchaser');
        const date = row.getAttribute('data-date');
        const rowText = row.textContent.toLowerCase();

        let showRow = true;

        // Filter by search text
        if (searchInput && !rowText.includes(searchInput)) {
            showRow = false;
        }

        // Filter by supplier
        if (supplierFilter && supplierID !== supplierFilter) {
            showRow = false;
        }

        // Filter by status
        if (statusFilter && status !== statusFilter) {
            showRow = false;
        }

        // Filter by purchaser
        if (purchaserFilter && purchaser !== purchaserFilter) {
            showRow = false;
        }

        // Filter by date range
        if (dateFromFilter && date < dateFromFilter) {
            showRow = false;
        }
        if (dateToFilter && date > dateToFilter) {
            showRow = false;
        }

        row.style.display = showRow ? '' : 'none';
    }
}

/**
 * Clear all filters
 */
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('supplierFilter').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('purchaserFilter').value = '';
    document.getElementById('dateFromFilter').value = '';
    document.getElementById('dateToFilter').value = '';

    // Reset table display
    const rows = document.querySelectorAll('#purchasesTable tbody tr');
    rows.forEach(row => row.style.display = 'table-row');
}

/**
 * Initialize purchases page functionality
 */
function initPurchasesPage() {
    // Search functionality
    if (typeof searchTable === 'function') {
        searchTable('searchInput', 'purchasesTable');
    }

    // Supplier filter
    const supplierFilter = document.getElementById('supplierFilter');
    if (supplierFilter) {
        supplierFilter.addEventListener('change', function() {
            const filter = this.value;
            const rows = document.querySelectorAll('#purchasesTable tbody tr[data-supplier-id]');

            rows.forEach(row => {
                const supplierId = row.getAttribute('data-supplier-id');
                if (filter === '' || supplierId === filter) {
                    row.style.display = 'table-row';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }

    // Date filters
    const dateFromFilter = document.getElementById('dateFromFilter');
    const dateToFilter = document.getElementById('dateToFilter');

    if (dateFromFilter && dateToFilter) {
        function filterByDate() {
            const fromDate = dateFromFilter.value;
            const toDate = dateToFilter.value;
            const rows = document.querySelectorAll('#purchasesTable tbody tr[data-date]');

            rows.forEach(row => {
                const rowDate = row.getAttribute('data-date');
                let show = true;

                if (fromDate && rowDate < fromDate) show = false;
                if (toDate && rowDate > toDate) show = false;

                row.style.display = show ? 'table-row' : 'none';
            });
        }

        dateFromFilter.addEventListener('change', filterByDate);
        dateToFilter.addEventListener('change', filterByDate);
    }

    // Initialize bulk delete functionality (admin only)
    if (typeof initBulkDelete === 'function') {
        initBulkDelete('purchasesTable', 'purchases', '/purchases/bulk-delete');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPurchasesPage);
} else {
    initPurchasesPage();
}

// Make functions globally available
window.printPurchase = printPurchase;
window.filterTable = filterTable;
window.clearFilters = clearFilters;
