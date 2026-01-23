/**
 * Formatting utilities for currency, dates, and other common formats
 */

/**
 * Format currency value
 * @param {number} amount - The amount to format
 * @param {string} currency - Currency code (default: USD)
 * @param {string} locale - Locale string (default: en-US)
 * @returns {string} Formatted currency string
 */
export function formatCurrency(amount, currency = 'USD', locale = 'en-US') {
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Format date string to local date
 * @param {string} dateString - ISO date string
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export function formatDate(dateString, options = {}) {
    if (!dateString) return '';

    const date = new Date(dateString);

    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };

    return date.toLocaleDateString(undefined, { ...defaultOptions, ...options });
}

/**
 * Format date to short format (MM/DD/YYYY)
 * @param {string} dateString - ISO date string
 * @returns {string} Short formatted date
 */
export function formatDateShort(dateString) {
    return formatDate(dateString, { year: 'numeric', month: '2-digit', day: '2-digit' });
}

/**
 * Format datetime to full timestamp
 * @param {string} dateString - ISO date string
 * @returns {string} Full timestamp
 */
export function formatDateTime(dateString) {
    if (!dateString) return '';

    const date = new Date(dateString);
    return date.toLocaleString();
}

/**
 * Format file size in bytes to human-readable format
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted file size
 */
export function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format number with thousand separators
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @param {string} suffix - Suffix to add (default: ...)
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength = 50, suffix = '...') {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * Capitalize first letter of each word
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
export function titleCase(str) {
    if (!str) return '';
    return str.replace(/\w\S*/g, (txt) =>
        txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    );
}
