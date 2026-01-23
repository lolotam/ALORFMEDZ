/**
 * Patients Management Module
 * Handles patients-specific functionality
 */

/**
 * Initialize patients page functionality
 */
function initPatientsPage() {
    // Initialize search functionality
    if (typeof searchTable === 'function') {
        searchTable('searchInput', 'patientsTable');
    }

    // Initialize bulk delete functionality
    if (typeof initBulkDelete === 'function') {
        initBulkDelete('patientsTable', 'patients', '/patients/bulk-delete');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPatientsPage);
} else {
    initPatientsPage();
}
