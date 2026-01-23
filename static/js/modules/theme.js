/**
 * Theme switching functionality (light/dark mode)
 */

/**
 * Toggle between light and dark theme
 */
export function toggleTheme() {
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

/**
 * Load saved theme and apply it
 */
export function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);

    const themeText = document.getElementById('theme-text');
    if (themeText) {
        themeText.textContent = savedTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
    }
}

// Initialize theme on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
} else {
    initTheme();
}
