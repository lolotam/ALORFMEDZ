/**
 * Hospital Pharmacy Management System - Main Application
 * Entry point for all JavaScript modules
 */

// Import all modules
import { initSidebar } from './modules/sidebar.js';
import { initTheme, toggleTheme } from './modules/theme.js';
import { initConfirmDelete, showConfirmDelete, initImportModal, showPreviewModal, loadPreviewFromUrl } from './modules/modals.js';
import { initTableSearch, filterTable, exportTableToCSV, exportPurchasesToCSV, exportConsumptionToCSV, exportConsumptionReportToCSV } from './modules/tables.js';
import { initBulkActions, performBulkDelete } from './modules/bulk-actions.js';
import { formatCurrency, formatDate, formatDateShort, formatDateTime, formatFileSize, formatNumber, truncateText, titleCase } from './utils/formatters.js';
import { showLoading, hideLoading, showAlert, confirmDelete, toggleElement, debounce, elementExists, getSelectedValues, serializeForm, copyToClipboard, printPage, scrollToElement } from './utils/helpers.js';

// Make functions globally available
window.toggleTheme = toggleTheme;
window.confirmDelete = confirmDelete;
window.showAlert = showAlert;
window.exportTableToCSV = exportTableToCSV;
window.exportPurchasesToCSV = exportPurchasesToCSV;
window.exportConsumptionToCSV = exportConsumptionToCSV;
window.exportConsumptionReportToCSV = exportConsumptionReportToCSV;
window.initBulkActions = initBulkActions;
window.performBulkDelete = performBulkDelete;
window.initTableSearch = initTableSearch;
window.filterTable = filterTable;
window.showConfirmDelete = showConfirmDelete;
window.showPreviewModal = showPreviewModal;
window.loadPreviewFromUrl = loadPreviewFromUrl;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.printPage = printPage;

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
});

console.log('Hospital Pharmacy Management System - JavaScript initialized');
