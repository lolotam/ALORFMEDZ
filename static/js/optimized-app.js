// Optimized Hospital Pharmacy Management System - JavaScript
// Performance-enhanced version with lazy loading, caching, and efficient DOM manipulation

class PerformanceManager {
    constructor() {
        this.cache = new Map();
        this.loadingStates = new Set();
        this.debounceTimers = new Map();
        this.lazyLoadObserver = null;
        this.init();
    }

    init() {
        this.setupLazyLoading();
        this.setupPerformanceMonitoring();
        this.preloadCriticalData();
    }

    // Debouncing utility for search and input handling
    debounce(func, delay, key) {
        if (this.debounceTimers.has(key)) {
            clearTimeout(this.debounceTimers.get(key));
        }

        const timer = setTimeout(() => {
            func();
            this.debounceTimers.delete(key);
        }, delay);

        this.debounceTimers.set(key, timer);
    }

    // Intelligent caching with TTL
    setCache(key, data, ttl = 300000) { // 5 minutes default
        this.cache.set(key, {
            data: data,
            timestamp: Date.now(),
            ttl: ttl
        });
    }

    getCache(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;

        if (Date.now() - cached.timestamp > cached.ttl) {
            this.cache.delete(key);
            return null;
        }

        return cached.data;
    }

    // Setup Intersection Observer for lazy loading
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            this.lazyLoadObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadLazyContent(entry.target);
                        this.lazyLoadObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '50px 0px'
            });
        }
    }

    loadLazyContent(element) {
        const endpoint = element.dataset.lazyEndpoint;
        if (endpoint && !this.loadingStates.has(endpoint)) {
            this.loadingStates.add(endpoint);
            this.fetchData(endpoint)
                .then(data => {
                    this.renderLazyContent(element, data);
                })
                .finally(() => {
                    this.loadingStates.delete(endpoint);
                });
        }
    }

    // Performance monitoring
    setupPerformanceMonitoring() {
        // Monitor long tasks
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    if (entry.duration > 50) {
                        console.warn(`Long task detected: ${entry.duration}ms`);
                    }
                });
            });
            observer.observe({entryTypes: ['longtask']});
        }
    }

    // Preload critical data
    preloadCriticalData() {
        const criticalEndpoints = [
            '/api/medicines/summary',
            '/api/stores/inventory/low-stock'
        ];

        criticalEndpoints.forEach(endpoint => {
            this.fetchData(endpoint, true); // Force cache
        });
    }

    // Optimized fetch with caching and error handling
    async fetchData(url, forceCache = false) {
        const cacheKey = `fetch_${url}`;

        if (!forceCache) {
            const cached = this.getCache(cacheKey);
            if (cached) return cached;
        }

        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;

        } catch (error) {
            console.error(`Fetch error for ${url}:`, error);
            throw error;
        }
    }

    renderLazyContent(element, data) {
        // Virtual scrolling for large lists
        if (data.length > 100) {
            this.renderVirtualList(element, data);
        } else {
            this.renderRegularList(element, data);
        }
    }

    // Virtual scrolling implementation
    renderVirtualList(container, items) {
        const itemHeight = 50; // Fixed height per item
        const containerHeight = container.clientHeight;
        const visibleCount = Math.ceil(containerHeight / itemHeight) + 5; // Buffer

        let scrollTop = 0;
        let startIndex = 0;

        const viewport = document.createElement('div');
        viewport.style.height = `${items.length * itemHeight}px`;
        viewport.style.position = 'relative';

        const visibleItems = document.createElement('div');
        visibleItems.style.position = 'absolute';
        visibleItems.style.top = '0';
        visibleItems.style.width = '100%';

        viewport.appendChild(visibleItems);
        container.appendChild(viewport);

        const updateVisible = () => {
            const newStartIndex = Math.floor(scrollTop / itemHeight);
            const newEndIndex = Math.min(newStartIndex + visibleCount, items.length);

            if (newStartIndex !== startIndex) {
                startIndex = newStartIndex;

                // Clear existing items
                visibleItems.innerHTML = '';

                // Render visible items
                for (let i = startIndex; i < newEndIndex; i++) {
                    const item = this.createListItem(items[i], i);
                    item.style.position = 'absolute';
                    item.style.top = `${i * itemHeight}px`;
                    item.style.height = `${itemHeight}px`;
                    visibleItems.appendChild(item);
                }
            }
        };

        container.addEventListener('scroll', (e) => {
            scrollTop = e.target.scrollTop;
            this.debounce(updateVisible, 16, 'virtualScroll'); // ~60fps
        });

        updateVisible(); // Initial render
    }

    renderRegularList(container, items) {
        const fragment = document.createDocumentFragment();
        items.forEach((item, index) => {
            fragment.appendChild(this.createListItem(item, index));
        });
        container.appendChild(fragment);
    }

    createListItem(item, index) {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${this.escapeHtml(item.name || 'Unknown')}</strong>
                    <small class="text-muted d-block">${this.escapeHtml(item.description || '')}</small>
                </div>
                <span class="badge bg-primary rounded-pill">${item.quantity || 0}</span>
            </div>
        `;
        return li;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

class OptimizedTableManager {
    constructor(tableSelector) {
        this.table = document.querySelector(tableSelector);
        this.currentPage = 1;
        this.pageSize = 25;
        this.totalItems = 0;
        this.filters = {};
        this.sortConfig = { column: null, direction: 'asc' };
        this.init();
    }

    init() {
        if (!this.table) return;

        this.setupPagination();
        this.setupSorting();
        this.setupFiltering();
        this.setupBulkActions();
    }

    setupPagination() {
        // Create pagination controls
        const paginationContainer = document.createElement('nav');
        paginationContainer.innerHTML = `
            <ul class="pagination justify-content-center" id="table-pagination">
                <!-- Pagination will be generated dynamically -->
            </ul>
        `;
        this.table.parentNode.appendChild(paginationContainer);
    }

    async loadPage(page = 1) {
        const params = new URLSearchParams({
            page: page,
            per_page: this.pageSize,
            ...this.filters
        });

        if (this.sortConfig.column) {
            params.append('sort', this.sortConfig.column);
            params.append('order', this.sortConfig.direction);
        }

        try {
            this.showLoadingState();
            const response = await performanceManager.fetchData(`${window.location.pathname}/api?${params}`);

            this.renderTable(response.data);
            this.updatePagination(response.pagination);
            this.currentPage = page;

        } catch (error) {
            this.showErrorState(error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    renderTable(data) {
        const tbody = this.table.querySelector('tbody');
        if (!tbody) return;

        // Use DocumentFragment for efficient DOM manipulation
        const fragment = document.createDocumentFragment();

        data.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = this.generateRowHTML(row);
            fragment.appendChild(tr);
        });

        // Clear and append all at once
        tbody.innerHTML = '';
        tbody.appendChild(fragment);
    }

    generateRowHTML(row) {
        // This would be customized based on the table type
        return `
            <td><input type="checkbox" class="form-check-input" value="${row.id}"></td>
            <td>${this.escapeHtml(row.name || '')}</td>
            <td>${this.escapeHtml(row.description || '')}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editItem('${row.id}')">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteItem('${row.id}')">Delete</button>
            </td>
        `;
    }

    updatePagination(pagination) {
        const paginationList = document.getElementById('table-pagination');
        if (!paginationList) return;

        let html = '';

        // Previous button
        html += `
            <li class="page-item ${!pagination.has_prev ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${pagination.page - 1}">Previous</a>
            </li>
        `;

        // Page numbers
        const startPage = Math.max(1, pagination.page - 2);
        const endPage = Math.min(pagination.total_pages, pagination.page + 2);

        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${i === pagination.page ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        // Next button
        html += `
            <li class="page-item ${!pagination.has_next ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${pagination.page + 1}">Next</a>
            </li>
        `;

        paginationList.innerHTML = html;

        // Attach event listeners
        paginationList.addEventListener('click', (e) => {
            e.preventDefault();
            if (e.target.classList.contains('page-link') && !e.target.parentElement.classList.contains('disabled')) {
                const page = parseInt(e.target.dataset.page);
                this.loadPage(page);
            }
        });
    }

    setupSorting() {
        const headers = this.table.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                const column = header.dataset.sort;

                if (this.sortConfig.column === column) {
                    this.sortConfig.direction = this.sortConfig.direction === 'asc' ? 'desc' : 'asc';
                } else {
                    this.sortConfig.column = column;
                    this.sortConfig.direction = 'asc';
                }

                this.updateSortIndicators();
                this.loadPage(1); // Reset to first page when sorting
            });
        });
    }

    updateSortIndicators() {
        // Clear all indicators
        this.table.querySelectorAll('th .sort-indicator').forEach(indicator => {
            indicator.remove();
        });

        // Add indicator to current sort column
        if (this.sortConfig.column) {
            const header = this.table.querySelector(`th[data-sort="${this.sortConfig.column}"]`);
            if (header) {
                const indicator = document.createElement('i');
                indicator.className = `bi bi-arrow-${this.sortConfig.direction === 'asc' ? 'up' : 'down'} sort-indicator`;
                header.appendChild(indicator);
            }
        }
    }

    setupFiltering() {
        const filterForm = document.getElementById('filter-form');
        if (!filterForm) return;

        filterForm.addEventListener('input', (e) => {
            performanceManager.debounce(() => {
                this.updateFilters();
                this.loadPage(1);
            }, 300, 'tableFilter');
        });
    }

    updateFilters() {
        const filterForm = document.getElementById('filter-form');
        if (!filterForm) return;

        this.filters = {};
        const formData = new FormData(filterForm);

        for (const [key, value] of formData.entries()) {
            if (value.trim()) {
                this.filters[key] = value.trim();
            }
        }
    }

    setupBulkActions() {
        const bulkActionButton = document.getElementById('bulk-action-btn');
        const selectAllCheckbox = document.getElementById('select-all');

        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                const checkboxes = this.table.querySelectorAll('tbody input[type="checkbox"]');
                checkboxes.forEach(cb => cb.checked = e.target.checked);
                this.updateBulkActionState();
            });
        }

        if (bulkActionButton) {
            bulkActionButton.addEventListener('click', () => {
                const selectedIds = this.getSelectedIds();
                if (selectedIds.length > 0) {
                    this.performBulkAction(selectedIds);
                }
            });
        }

        // Monitor individual checkbox changes
        this.table.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox') {
                this.updateBulkActionState();
            }
        });
    }

    getSelectedIds() {
        const checkboxes = this.table.querySelectorAll('tbody input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    updateBulkActionState() {
        const selectedCount = this.getSelectedIds().length;
        const bulkActionButton = document.getElementById('bulk-action-btn');

        if (bulkActionButton) {
            bulkActionButton.disabled = selectedCount === 0;
            bulkActionButton.textContent = `Bulk Action (${selectedCount})`;
        }
    }

    async performBulkAction(selectedIds) {
        if (!confirm(`Are you sure you want to perform this action on ${selectedIds.length} items?`)) {
            return;
        }

        try {
            const response = await fetch('/api/bulk-delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ ids: selectedIds })
            });

            if (response.ok) {
                this.loadPage(this.currentPage); // Refresh current page
                this.showSuccess(`Successfully processed ${selectedIds.length} items`);
            } else {
                throw new Error('Bulk action failed');
            }
        } catch (error) {
            this.showError(error.message);
        }
    }

    showLoadingState() {
        const tbody = this.table.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="100%" class="text-center">Loading...</td></tr>';
        }
    }

    hideLoadingState() {
        // Loading state will be replaced by actual data
    }

    showErrorState(message) {
        const tbody = this.table.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="100%" class="text-center text-danger">Error: ${message}</td></tr>`;
        }
    }

    showSuccess(message) {
        // You could integrate with a toast notification system
        console.log('Success:', message);
    }

    showError(message) {
        // You could integrate with a toast notification system
        console.error('Error:', message);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global instances
const performanceManager = new PerformanceManager();
let tableManager = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize optimized table management
    const mainTable = document.querySelector('.data-table');
    if (mainTable) {
        tableManager = new OptimizedTableManager('.data-table');
        tableManager.loadPage(1);
    }

    // Initialize lazy loading for any lazy elements
    document.querySelectorAll('[data-lazy-endpoint]').forEach(element => {
        if (performanceManager.lazyLoadObserver) {
            performanceManager.lazyLoadObserver.observe(element);
        }
    });

    // Original sidebar functionality (optimized)
    initializeSidebar();

    // Theme functionality
    initializeTheme();
});

function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    if (!sidebarToggle || !sidebar) return;

    // Use passive event listeners for better performance
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('show');
        if (sidebarOverlay) {
            sidebarOverlay.classList.toggle('show');
        }
    }, { passive: true });

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
        }, { passive: true });
    }

    // Optimized responsive handling
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (window.innerWidth > 992) {
                sidebar.classList.remove('show');
                if (sidebarOverlay) {
                    sidebarOverlay.classList.remove('show');
                }
            }
        }, 250);
    }, { passive: true });
}

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);

    const themeText = document.getElementById('theme-text');
    if (themeText) {
        themeText.textContent = savedTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
    }
}

function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    html.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    const themeText = document.getElementById('theme-text');
    if (themeText) {
        themeText.textContent = newTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
    }
}

// Optimized utility functions
const utils = {
    confirmDelete(message = 'Are you sure you want to delete this item?') {
        return confirm(message);
    },

    async submitForm(formSelector, options = {}) {
        const form = document.querySelector(formSelector);
        if (!form) return;

        const formData = new FormData(form);
        const url = options.url || form.action;
        const method = options.method || form.method || 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const result = await response.json();
                if (options.onSuccess) {
                    options.onSuccess(result);
                }
                return result;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            if (options.onError) {
                options.onError(error);
            }
            console.error('Form submission error:', error);
        }
    }
};

// Export for use in other modules
window.HospitalPMS = {
    performanceManager,
    tableManager,
    utils
};