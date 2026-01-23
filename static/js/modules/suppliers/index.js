/**
 * Suppliers Management Module
 * Handles suppliers-specific functionality
 */

/**
 * Toggle between card and table view
 * @param {string} view - 'card' or 'table'
 */
function toggleView(view) {
    const cardView = document.getElementById('cardView');
    const tableView = document.getElementById('tableView');
    const cardBtn = document.getElementById('cardViewBtn');
    const tableBtn = document.getElementById('tableViewBtn');

    if (view === 'card') {
        cardView.style.display = 'block';
        tableView.style.display = 'none';
        cardBtn.classList.add('active');
        tableBtn.classList.remove('active');
    } else {
        cardView.style.display = 'none';
        tableView.style.display = 'block';
        cardBtn.classList.remove('active');
        tableBtn.classList.add('active');
    }
}

/**
 * Filter suppliers table and cards
 */
function filterTable() {
    const searchInput = document.getElementById('searchInput');
    const typeFilter = document.getElementById('typeFilter');

    if (!searchInput || !typeFilter) return;

    const searchValue = searchInput.value.toLowerCase();
    const typeValue = typeFilter.value;

    // Filter cards
    const cards = document.querySelectorAll('.supplier-card');
    cards.forEach(function(card) {
        const name = card.getAttribute('data-name') || '';
        const type = card.getAttribute('data-type') || '';

        let showCard = true;
        if (searchValue && !name.includes(searchValue)) showCard = false;
        if (typeValue && type !== typeValue) showCard = false;

        card.style.display = showCard ? '' : 'none';
    });

    // Filter table rows
    const table = document.getElementById('suppliersTable');
    if (table) {
        const tbody = table.getElementsByTagName('tbody')[0];
        const rows = tbody.getElementsByTagName('tr');

        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName('td');

            if (cells.length === 0) continue;

            let showRow = true;

            // Search filter
            if (searchValue) {
                const name = cells[1].textContent.toLowerCase();
                const type = cells[2].textContent.toLowerCase();
                const contact = cells[3].textContent.toLowerCase();
                const phone = cells[4].textContent.toLowerCase();
                const email = cells[5].textContent.toLowerCase();
                const address = cells[6].textContent.toLowerCase();
                const notes = cells[7].textContent.toLowerCase();

                if (!name.includes(searchValue) &&
                    !type.includes(searchValue) &&
                    !contact.includes(searchValue) &&
                    !phone.includes(searchValue) &&
                    !email.includes(searchValue) &&
                    !address.includes(searchValue) &&
                    !notes.includes(searchValue)) {
                    showRow = false;
                }
            }

            // Type filter
            if (showRow && typeValue) {
                const rowType = row.getAttribute('data-type');
                if (rowType !== typeValue) showRow = false;
            }

            row.style.display = showRow ? '' : 'none';
        }
    }
}

/**
 * Initialize suppliers page functionality
 */
function initSuppliersPage() {
    const searchInput = document.getElementById('searchInput');
    const typeFilter = document.getElementById('typeFilter');

    if (searchInput) {
        searchInput.addEventListener('input', filterTable);
    }

    if (typeFilter) {
        typeFilter.addEventListener('change', filterTable);
    }

    // Initialize bulk delete functionality
    if (typeof initBulkDelete === 'function') {
        initBulkDelete('suppliersTable', 'suppliers', '/suppliers/bulk-delete');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSuppliersPage);
} else {
    initSuppliersPage();
}

// Make functions globally available
window.toggleView = toggleView;
window.filterTable = filterTable;
