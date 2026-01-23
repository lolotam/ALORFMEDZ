/**
 * Doctors Management Module
 * Handles doctors-specific functionality
 */

/**
 * Filter doctors table
 */
function filterTable() {
    const specialistFilter = document.getElementById('specialistFilter');
    const genderFilter = document.getElementById('genderFilter');
    const typeFilter = document.getElementById('typeFilter');
    const searchInput = document.getElementById('searchInput');

    if (!specialistFilter || !genderFilter || !typeFilter || !searchInput) return;

    const table = document.getElementById('doctorsTable');
    const tbody = table.getElementsByTagName('tbody')[0];
    const rows = tbody.getElementsByTagName('tr');

    const specialistValue = specialistFilter.value.toLowerCase();
    const genderValue = genderFilter.value.toLowerCase();
    const typeValue = typeFilter.value.toLowerCase();
    const searchValue = searchInput.value.toLowerCase();

    for (let i = 0; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.getElementsByTagName('td');

        if (cells.length === 0) continue;

        let showRow = true;

        // Search filter
        if (searchValue) {
            const doctorName = cells[1].textContent.toLowerCase();
            const specialization = cells[2].textContent.toLowerCase();
            const department = cells[3].textContent.toLowerCase();
            const qualification = cells[4].textContent.toLowerCase();
            const phone = cells[6].textContent.toLowerCase();
            const email = cells[7].textContent.toLowerCase();
            const notes = cells[9].textContent.toLowerCase();

            if (!doctorName.includes(searchValue) &&
                !specialization.includes(searchValue) &&
                !department.includes(searchValue) &&
                !qualification.includes(searchValue) &&
                !phone.includes(searchValue) &&
                !email.includes(searchValue) &&
                !notes.includes(searchValue)) {
                showRow = false;
            }
        }

        // Specialist filter
        if (showRow && specialistValue !== '') {
            const specialistFromRow = row.getAttribute('data-specialist');
            if (!specialistFromRow || !specialistFromRow.includes(specialistValue)) {
                showRow = false;
            }
        }

        // Gender filter
        if (showRow && genderValue !== '') {
            const genderFromRow = row.getAttribute('data-gender');
            if (genderFromRow !== genderValue) {
                showRow = false;
            }
        }

        // Type filter
        if (showRow && typeValue !== '') {
            const typeFromRow = row.getAttribute('data-type');
            if (typeFromRow !== typeValue) {
                showRow = false;
            }
        }

        row.style.display = showRow ? '' : 'none';
    }
}

/**
 * Initialize doctors page functionality
 */
function initDoctorsPage() {
    // Initialize search functionality
    if (typeof searchTable === 'function') {
        searchTable('searchInput', 'doctorsTable');
    }

    // Initialize filter functionality
    const specialistFilter = document.getElementById('specialistFilter');
    const genderFilter = document.getElementById('genderFilter');
    const typeFilter = document.getElementById('typeFilter');
    const searchInput = document.getElementById('searchInput');

    if (specialistFilter) {
        specialistFilter.addEventListener('change', filterTable);
    }

    if (genderFilter) {
        genderFilter.addEventListener('change', filterTable);
    }

    if (typeFilter) {
        typeFilter.addEventListener('change', filterTable);
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterTable);
    }

    // Initialize bulk delete functionality
    if (typeof initBulkDelete === 'function') {
        initBulkDelete('doctorsTable', 'doctors', '/doctors/bulk-delete');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDoctorsPage);
} else {
    initDoctorsPage();
}

// Make functions globally available
window.filterTable = filterTable;
