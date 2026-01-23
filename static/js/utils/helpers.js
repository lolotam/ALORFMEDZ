/**
 * Helper utilities for common operations
 */

/**
 * Show loading spinner on button
 * @param {string} buttonId - ID of button element
 */
export function showLoading(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Loading...';
    }
}

/**
 * Hide loading spinner on button
 * @param {string} buttonId - ID of button element
 * @param {string} originalText - Original button text to restore
 */
export function hideLoading(buttonId, originalText) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

/**
 * Show alert message
 * @param {string} type - Alert type (success, danger, warning, info)
 * @param {string} message - Alert message
 * @param {number} autoHide - Auto-hide delay in ms (0 to disable)
 */
export function showAlert(type, message, autoHide = 5000) {
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
        if (mainContent) {
            mainContent.insertBefore(alertContainer, mainContent.firstChild);
        }
    }

    alertContainer.appendChild(alertDiv);

    // Auto-dismiss
    if (autoHide > 0) {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alertDiv);
            bsAlert.close();
        }, autoHide);
    }
}

/**
 * Confirm delete action
 * @param {string} message - Custom confirmation message
 * @returns {boolean} Confirmation result
 */
export function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

/**
 * Toggle element visibility
 * @param {string} elementId - ID of element
 * @param {boolean} show - Whether to show or hide
 */
export function toggleElement(elementId, show) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = show ? '' : 'none';
    }
}

/**
 * Debounce function calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Check if element exists in DOM
 * @param {string} elementId - ID of element
 * @returns {boolean} True if element exists
 */
export function elementExists(elementId) {
    return document.getElementById(elementId) !== null;
}

/**
 * Get selected values from multiple select
 * @param {string} selectId - ID of select element
 * @returns {Array} Array of selected values
 */
export function getSelectedValues(selectId) {
    const select = document.getElementById(selectId);
    if (!select) return [];
    return Array.from(select.selectedOptions).map(option => option.value);
}

/**
 * Serialize form data
 * @param {HTMLFormElement} form - Form element
 * @returns {Object} Form data as object
 */
export function serializeForm(form) {
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
        if (data[key]) {
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }
    return data;
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise} Promise that resolves when done
 */
export async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('success', 'Copied to clipboard!');
    } catch (err) {
        console.error('Failed to copy: ', err);
        showAlert('danger', 'Failed to copy to clipboard');
    }
}

/**
 * Print page
 */
export function printPage() {
    window.print();
}

/**
 * Scroll to element
 * @param {string} elementId - ID of element to scroll to
 * @param {number} offset - Offset from top in pixels
 */
export function scrollToElement(elementId, offset = 0) {
    const element = document.getElementById(elementId);
    if (element) {
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
}
