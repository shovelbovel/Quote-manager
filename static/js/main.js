/**
 * Main JavaScript file for Devis Manager Application
 */

/**
 * Initialize modal functionality
 */
function initializeModals() {
    // Open modal when button with data-toggle="modal" is clicked
    const modalTriggers = document.querySelectorAll('[data-toggle="modal"]');
    
    modalTriggers.forEach(trigger => {
        const targetSelector = trigger.getAttribute('data-target');
        const modal = document.querySelector(targetSelector);
        
        if (modal) {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                modal.classList.add('active');
                document.body.style.overflow = 'hidden'; // Prevent background scroll
            });
            
            // Close modal when clicking close button
            const closeButton = modal.querySelector('.close');
            if (closeButton) {
                closeButton.addEventListener('click', function() {
                    modal.classList.remove('active');
                    document.body.style.overflow = ''; // Restore scroll
                });
            }
            
            // Close modal when clicking outside modal content
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    modal.classList.remove('active');
                    document.body.style.overflow = ''; // Restore scroll
                }
            });
        }
    });
}

/**
 * Initialize user action buttons functionality
 */
function initializeUserActions() {
    const userTable = document.querySelector('.admin-users-page .table');
    if (!userTable) return;

    // Edit User
    userTable.querySelectorAll('.dropdown-menu a.dropdown-item').forEach(item => {
        const actionText = item.textContent.trim();
        if (actionText === 'Edit User') {
            // Do not attach click handler to allow normal link navigation
            return;
        }
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const row = this.closest('tr');
            const userId = row.getAttribute('data-user-id');
            console.log('User action clicked:', actionText, 'User ID:', userId);
            if (!userId) {
                console.error('User ID not found for action:', actionText);
                return;
            }

            if (actionText === 'Deactivate' || actionText === 'Activate') {
                fetch(`/users/${userId}/toggle-active/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    credentials: 'include'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert(`User ${actionText.toLowerCase()}d successfully.`);
                        location.reload();
                    } else {
                        alert('Failed to update user status.');
                    }
                })
                .catch(error => {
                    console.error('Error toggling user active status:', error);
                    alert('An error occurred.');
                });
            } else if (actionText === 'Make Admin' || actionText === 'Remove Admin') {
                fetch(`/users/${userId}/toggle-admin/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    credentials: 'include'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert(`User admin status updated successfully.`);
                        location.reload();
                    } else {
                        alert('Failed to update admin status.');
                    }
                })
                .catch(error => {
                    console.error('Error toggling user admin status:', error);
                    alert('An error occurred.');
                });
            } else if (actionText === 'Delete') {
                if (confirm('Are you sure you want to delete this user?')) {
                    fetch(`/users/${userId}/delete/`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCsrfToken()
                        },
                        credentials: 'include'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            alert('User deleted successfully.');
                            location.reload();
                        } else {
                            alert('Failed to delete user.');
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting user:', error);
                        alert('An error occurred.');
                    });
                }
            }
        });
    });
}

console.log('main.js script loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded event fired');
    
    // Debug: Check if the dropdown toggle exists
    const toggle = document.querySelector('.dropdown-toggle');
    console.log('Dropdown toggle element:', toggle);
    
    // Initialize all components
    console.log('Initializing navigation...');
    try {
        initializeNavigation();
        console.log('Navigation initialized');
        
        // Initialize other components
        initializeTabSystem();
        initializeNotifications();
        initializeQuoteItems();
        initializeStatusChangeAnimations();
        initializeForms();
        initializeModals();
        initializeUserActions();
        
        console.log('All components initialized');
    } catch (error) {
        console.error('Error during initialization:', error);
    }
});

// Also try to run when window loads as a fallback
window.addEventListener('load', function() {
    console.log('Window loaded, running initialization');
    initializeNavigation();
});

/**
 * Initialize navigation functionality
 */
function initializeNavigation() {
    console.log('Navigation initialization started');
    
    // Function to close all dropdowns
    function closeAllDropdowns(exceptMenu = null) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            if (menu !== exceptMenu) {
                menu.classList.remove('show');
            }
        });
    }
    
    // Handle dropdown toggle clicks
    document.addEventListener('click', function(e) {
        const toggle = e.target.closest('.dropdown-toggle');
        const dropdown = e.target.closest('.dropdown');
        
        // If clicking a dropdown toggle
        if (toggle) {
            e.preventDefault();
            e.stopPropagation();
            
            const menu = toggle.nextElementSibling;
            const isMenuVisible = menu.classList.contains('show');
            
            console.log('Menu element:', menu);
            console.log('Current classes:', menu.className);
            
            // Close all dropdowns first
            closeAllDropdowns();
            
            // Toggle the clicked dropdown
            if (!isMenuVisible) {
                menu.classList.add('show');
                console.log('Dropdown shown. New classes:', menu.className);
                // Force a reflow to ensure the transition works
                void menu.offsetWidth;
            } else {
                console.log('Dropdown was already visible');
            }
            
            return;
        }
        
        // If clicking a dropdown item
        if (e.target.closest('.dropdown-item')) {
            const menu = e.target.closest('.dropdown-menu');
            if (menu) {
                menu.classList.remove('show');
            }
            return;
        }
        
        // If clicking outside any dropdown
        if (!dropdown) {
            closeAllDropdowns();
        }
    });
    
    // Close dropdowns when pressing Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllDropdowns();
        }
    });
    
    console.log('Navigation initialization complete');
}
/**
 * Initialize tab system for pages with tabbed content
 */
function initializeTabSystem() {
    const tabContainers = document.querySelectorAll('.tabs-container');
    
    tabContainers.forEach(container => {
        const tabs = container.querySelectorAll('.tab');
        const tabContents = container.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Remove active class from all tabs and contents
                tabs.forEach(t => t.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                // Add active class to current tab and corresponding content
                const tabId = this.getAttribute('data-tab');
                this.classList.add('active');
                
                const activeContent = container.querySelector(`.tab-content[data-tab="${tabId}"]`);
                if (activeContent) {
                    activeContent.classList.add('active');
                }
            });
        });
    });
}

/**
 * Initialize notification system
 */
function initializeNotifications() {
    // Mark notification as read when clicked
    const notifications = document.querySelectorAll('.notification');
    
    notifications.forEach(notification => {
        const closeBtn = notification.querySelector('.notification-close');
        
        if (closeBtn) {
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Get notification ID
                const notificationId = notification.getAttribute('data-id');
                
                // Make API call to mark as read
                fetch(`/api/notifications/${notificationId}/mark_read/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .then(response => {
                    if (response.ok) {
                        // Remove notification with animation
                        notification.style.opacity = '0';
                        notification.style.height = '0';
                        notification.style.margin = '0';
                        notification.style.padding = '0';
                        
                        setTimeout(() => {
                            notification.remove();
                        }, 300);
                    }
                })
                .catch(error => {
                    console.error('Error marking notification as read:', error);
                });
            });
        }
        
        // Mark as read when clicked anywhere (except close button)
        notification.addEventListener('click', function(e) {
            if (e.target !== closeBtn && !closeBtn.contains(e.target)) {
                notification.classList.remove('unread');
                
                // Get notification ID
                const notificationId = notification.getAttribute('data-id');
                
                // Make API call to mark as read
                fetch(`/api/notifications/${notificationId}/mark_read/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .catch(error => {
                    console.error('Error marking notification as read:', error);
                });
            }
        });
    });
    
    // Mark all as read button
    const markAllReadBtn = document.querySelector('.mark-all-read');
    
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            fetch('/api/notifications/mark_all_read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => {
                if (response.ok) {
                    // Update UI
                    const unreadNotifications = document.querySelectorAll('.notification.unread');
                    unreadNotifications.forEach(notification => {
                        notification.classList.remove('unread');
                    });
                    
                    // Update counter if exists
                    const counter = document.querySelector('.notification-counter');
                    if (counter) {
                        counter.textContent = '0';
                        counter.style.display = 'none';
                    }
                }
            })
            .catch(error => {
                console.error('Error marking all notifications as read:', error);
            });
        });
    }
}

/**
 * Initialize quote items functionality (add, remove, update)
 */
function initializeQuoteItems() {
    const itemsForm = document.querySelector('.quote-items-form');
    
    if (!itemsForm) return;
    
    // Add new item row
    const addItemBtn = document.querySelector('.add-item-btn');
    const itemsContainer = document.querySelector('.items-container');
    const itemTemplate = document.querySelector('#item-template');
    
    if (addItemBtn && itemsContainer && itemTemplate) {
        // Add click handler for adding new items
        addItemBtn.addEventListener('click', function(e) {
            e.preventDefault();
            addNewItem(itemsContainer, itemTemplate);
        });
        
        // Add initial item if none exist
        const existingItems = itemsContainer.querySelectorAll('.item-row');
        if (existingItems.length === 0) {
            addNewItem(itemsContainer, itemTemplate);
        } else {
            existingItems.forEach(item => initializeItemRow(item));
        }
    }
    
    // Form submission
    itemsForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate form
        if (!validateQuoteForm(itemsForm)) {
            return false;
        }
        
        // Show loading state
        const submitBtn = itemsForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        const isEdit = itemsForm.action.includes('edit');
        const actionText = isEdit ? 'Updating' : 'Creating';
        
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${actionText}...`;
        
        try {
            // Prepare form data
            const formData = new FormData(itemsForm);
            
            // Log the data being sent (for debugging)
            console.log('Submitting form with data:', {
                title: formData.get('title'),
                client_name: formData.get('client_name'),
                client_email: formData.get('client_email'),
                status: formData.get('status')
            });
            
            // Submit via AJAX
            const response = await fetch(itemsForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `Failed to ${isEdit ? 'update' : 'create'} quote`);
            }
            
            if (data.redirect) {
                window.location.href = data.redirect;
            } else {
                showAlert('success', `Quote ${isEdit ? 'updated' : 'created'} successfully!`);
                if (!isEdit) {
                    setTimeout(() => {
                        window.location.href = data.redirect || '/quotes/';
                    }, 1500);
                }
            }
            
        } catch (error) {
            console.error('Error:', error);
            showAlert('danger', error.message || `An error occurred while ${isEdit ? 'updating' : 'creating'} the quote`);
        } finally {
            // Restore button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
}

/**
 * Add a new item row to the quote
 */
function addNewItem(container, template) {
    const newItem = template.content.cloneNode(true);
    const itemRow = newItem.querySelector('.item-row');
    container.appendChild(newItem);
    initializeItemRow(itemRow);
    
    // Focus the service select
    const serviceSelect = itemRow.querySelector('.item-service');
    if (serviceSelect) {
        serviceSelect.focus();
    }
    
    updateQuoteTotals();
}

/**
 * Validate the quote form
 */
function validateQuoteForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    // Validate at least one item
    const itemRows = form.querySelectorAll('.item-row');
    if (itemRows.length === 0) {
        showAlert('warning', 'Please add at least one item to the quote');
        return false;
    }
    
    // Validate each item
    itemRows.forEach(row => {
        const service = row.querySelector('.item-service');
        const quantity = row.querySelector('.item-quantity');
        const price = row.querySelector('.item-price');
        
        if (!service.value) {
            service.classList.add('is-invalid');
            isValid = false;
        }
        
        if (!quantity.value || parseFloat(quantity.value) <= 0) {
            quantity.classList.add('is-invalid');
            isValid = false;
        }
        
        if (!price.value || parseFloat(price.value) < 0) {
            price.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Initialize functionality for a single quote item row
 */
function initializeItemRow(itemRow) {
    if (!itemRow) return;
    
    // Get elements
    const quantityInput = itemRow.querySelector('.item-quantity');
    const priceInput = itemRow.querySelector('.item-price');
    const totalElement = itemRow.querySelector('.item-total');
    const totalInput = itemRow.querySelector('.item-total-input');
    const serviceSelect = itemRow.querySelector('.item-service');
    const removeBtn = itemRow.querySelector('.remove-item-btn');
    
    // Format number to 2 decimal places
    const formatNumber = (num) => {
        const numValue = parseFloat(num);
        return isNaN(numValue) ? '0.00' : numValue.toFixed(2);
    };
    
    // Update item total when quantity or price changes
    const updateItemTotal = () => {
        if (!quantityInput || !priceInput || !totalElement) return;
        
        const quantity = parseFloat(quantityInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const total = quantity * price;
        
        // Update display and hidden input
        totalElement.textContent = formatNumber(total);
        if (totalInput) {
            totalInput.value = formatNumber(total);
        }
        
        // Update the quote total
        updateQuoteTotals();
    };
    
    // Handle quantity changes
    if (quantityInput) {
        quantityInput.addEventListener('input', function() {
            let value = this.value;
            // Remove any non-digit characters
            value = value.replace(/[^0-9]/g, '');
            // Ensure it's at least 1
            value = Math.max(1, parseInt(value) || 1);
            this.value = value;
            updateItemTotal();
        });
        
        // Handle arrow keys for increment/decrement
        quantityInput.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.stepUp();
                updateItemTotal();
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (parseInt(this.value) > 1) {
                    this.stepDown();
                    updateItemTotal();
                }
            }
        });
    }
    
    // Handle price changes
    if (priceInput) {
        priceInput.addEventListener('input', function() {
            // Format as user types
            let value = this.value;
            // Remove any non-digit or decimal characters
            value = value.replace(/[^0-9.]/g, '');
            // Ensure only one decimal point
            const parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            
            // Limit to 2 decimal places
            if (parts.length === 2 && parts[1].length > 2) {
                value = parts[0] + '.' + parts[1].substring(0, 2);
            }
            
            this.value = value;
            updateItemTotal();
        });
        
        // Format on blur
        priceInput.addEventListener('blur', function() {
            const value = parseFloat(this.value) || 0;
            this.value = formatNumber(value);
            updateItemTotal();
        });
    }
    
    // Update price based on selected service
    if (serviceSelect) {
        serviceSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const price = parseFloat(selectedOption.getAttribute('data-price')) || 0;
            
            if (price > 0) {
                priceInput.value = formatNumber(price);
                updateItemTotal();
                
                // Auto-focus quantity field
                if (quantityInput) {
                    quantityInput.focus();
                    quantityInput.select();
                }
            }
        });
        
        // Trigger change event if a service is already selected
        if (serviceSelect.value) {
            serviceSelect.dispatchEvent(new Event('change'));
        }
    }
    
    // Handle remove button
    if (removeBtn) {
        removeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // If it's the last item, don't remove it, just clear it
            const allRows = document.querySelectorAll('.item-row');
            if (allRows.length === 1) {
                const row = allRows[0];
                row.querySelector('.item-service').value = '';
                row.querySelector('.item-description').value = '';
                row.querySelector('.item-quantity').value = '1';
                row.querySelector('.item-price').value = '0.00';
                updateItemTotal();
                return;
            }
            
            // For existing items, we might want to confirm deletion
            const itemId = itemRow.getAttribute('data-id');
            if (itemId && !itemId.startsWith('new-')) {
                if (!confirm('Are you sure you want to remove this item?')) {
                    return;
                }
            }
            
            // Remove with animation
            itemRow.style.opacity = '0';
            setTimeout(() => {
                itemRow.remove();
                updateQuoteTotals();
            }, 300);
        });
    }
    
    // Initialize the total
    updateItemTotal();
}

/**
 * Update quote totals based on item totals
 */
function updateQuoteTotals() {
    let subtotal = 0;
    let itemCount = 0;
    
    // Calculate subtotal from all items
    document.querySelectorAll('.item-row').forEach(row => {
        const quantityInput = row.querySelector('.item-quantity');
        const priceInput = row.querySelector('.item-price');
        const totalElement = row.querySelector('.item-total');
        const totalInput = row.querySelector('.item-total-input');
        
        // Skip if required elements are missing
        if (!quantityInput || !priceInput || !totalElement) return;
        
        const quantity = parseFloat(quantityInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const total = quantity * price;
        
        // Only add to subtotal if it's a valid item (has a service selected)
        const serviceSelect = row.querySelector('.item-service');
        if (serviceSelect && serviceSelect.value) {
            subtotal += total;
            itemCount++;
        }
        
        // Update the row's total display
        const formattedTotal = formatNumber(total);
        totalElement.textContent = formattedTotal;
        if (totalInput) {
            totalInput.value = formattedTotal;
        }
    });
    
    // Update subtotal display
    const subtotalElement = document.querySelector('.subtotal-amount');
    if (subtotalElement) {
        subtotalElement.textContent = formatNumber(subtotal);
    }
    
    // Calculate tax (assuming 20% tax rate)
    const taxRate = 0.20;
    const tax = subtotal * taxRate;
    const grandTotal = subtotal + tax;
    
    // Update tax and grand total displays
    const taxElement = document.querySelector('.tax-amount');
    const grandTotalElement = document.querySelector('.grand-total-amount');
    const quoteTotalElement = document.querySelector('.quote-total-amount');
    const itemsCountElement = document.querySelector('.items-count');
    
    if (taxElement) taxElement.textContent = formatNumber(tax);
    if (grandTotalElement) grandTotalElement.textContent = formatNumber(grandTotal);
    if (quoteTotalElement) quoteTotalElement.textContent = formatNumber(grandTotal);
    if (itemsCountElement) itemsCountElement.textContent = itemCount;
    
    // Update hidden input for form submission
    const totalInput = document.querySelector('input[name="total_amount"]');
    if (totalInput) {
        totalInput.value = formatNumber(grandTotal);
    }
    
    // Update the submit button state based on validation
    const submitBtn = document.querySelector('button[type="submit"]');
    if (submitBtn) {
        const isValid = itemCount > 0 && subtotal > 0;
        submitBtn.disabled = !isValid;
    }
    
    return grandTotal;
}

/**
 * Initialize animations for status changes
 */
function initializeStatusChangeAnimations() {
    const statusSelect = document.querySelector('.status-select');
    
    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            const status = this.value;
            const statusBadge = document.querySelector('.status-badge');
            
            if (statusBadge) {
                // Remove all status classes
                statusBadge.classList.remove('badge-pending', 'badge-accepted', 'badge-refused');
                
                // Add the new status class
                statusBadge.classList.add(`badge-${status}`);
                
                // Update text
                statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
                
                // Add animation
                statusBadge.classList.add('fade-in');
                setTimeout(() => {
                    statusBadge.classList.remove('fade-in');
                }, 500);
            }
        });
    }
}

/**
 * Initialize dashboard charts and data
 */
function initializeDashboard() {
    // Chart.js could be implemented here for analytics
    console.log('Dashboard initialized');
    
    // Example: Update stats with fade-in animation
    const statValues = document.querySelectorAll('.stat-value');
    
    statValues.forEach((stat, index) => {
        setTimeout(() => {
            stat.classList.add('fade-in');
        }, index * 100);
    });
}

/**
 * Initialize quote detail page functionality
 */
function initializeQuoteDetail() {
    // Status change confirmation and submission
    const statusForm = document.querySelector('.status-change-form');
    
    if (statusForm) {
        const statusSelect = statusForm.querySelector('.status-select');
        const submitButton = statusForm.querySelector('button[type="submit"]');
        
        statusForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const originalStatus = statusSelect.getAttribute('data-original');
            const newStatus = statusSelect.value;
            
            if (originalStatus === newStatus) {
                return; // No change, do nothing
            }
            
            if (!confirm(`Are you sure you want to change the status to ${newStatus}?`)) {
                return;
            }
            
            // Disable the button and show loading state
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
            
            try {
                const formData = new FormData(statusForm);
                const response = await fetch(statusForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCsrfToken()
                    }
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Update the original status to the new one
                    statusSelect.setAttribute('data-original', newStatus);
                    
                    // Update the status badge
                    const statusBadge = document.querySelector('.status-badge');
                    if (statusBadge) {
                        // Remove all status classes
                        statusBadge.classList.remove('badge-pending', 'badge-accepted', 'badge-refused');
                        // Add the new status class
                        statusBadge.classList.add(`badge-${newStatus}`);
                        // Update the text
                        statusBadge.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
                    }
                    
                    showAlert('success', data.message || 'Status updated successfully');
                } else {
                    throw new Error(data.error || 'Failed to update status');
                }
            } catch (error) {
                console.error('Error updating status:', error);
                showAlert('danger', error.message || 'An error occurred while updating the status');
                // Revert the select to the original value
                statusSelect.value = originalStatus;
            } finally {
                // Re-enable the button and restore the original text
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }
        });
    }
    
    // Share quote functionality
    const shareForm = document.querySelector('.share-form');
    
    if (shareForm) {
        shareForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[name="email"]').value;
            const quoteId = this.getAttribute('data-quote-id');
            
            fetch(`/api/quotes/${quoteId}/share/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ email })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showAlert('success', data.message);
                    this.reset();
                } else if (data.error) {
                    showAlert('danger', data.error);
                }
            })
            .catch(error => {
                console.error('Error sharing quote:', error);
                showAlert('danger', 'An error occurred. Please try again.');
            });
        });
    }
    
    // Export functionality
    const exportButtons = document.querySelectorAll('.export-btn');
    
    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const format = this.getAttribute('data-format');
            const quoteId = this.getAttribute('data-quote-id');
            
            fetch(`/api/quotes/${quoteId}/export-${format}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                }
            })
            .then(response => {
                if (format === 'pdf' || format === 'excel') {
                    return response.blob();
                }
                return response.json();
            })
            .then(data => {
                if (data instanceof Blob) {
                    // Create download link
                    const url = window.URL.createObjectURL(data);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `quote-${quoteId}.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                } else if (data.message) {
                    showAlert('success', data.message);
                } else if (data.error) {
                    showAlert('danger', data.error);
                }
            })
            .catch(error => {
                console.error(`Error exporting to ${format}:`, error);
                showAlert('danger', 'An error occurred. Please try again.');
            });
        });
    });
}

/**
 * Initialize form validation and enhancements
 */
function initializeForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Only initialize custom validation if the form has data-validate attribute
        if (form.hasAttribute('data-validate')) {
            form.addEventListener('submit', function(e) {
                if (!validateForm(this)) {
                    e.preventDefault();
                    showAlert('warning', 'Please check the form for errors');
                }
            });
            
            // Initialize validation for each input
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    validateInput(this);
                });
                
                input.addEventListener('input', function() {
                    // Clear error if input is valid
                    if (this.validity.valid) {
                        clearInputError(this);
                    }
                });
            });
        }
    });
}

/**
 * Validate a single form input
 */
function validateInput(input) {
    if (input.type === 'hidden') return true;
    
    clearInputError(input);
    
    // Check if input is required and empty
    if (input.required && !input.value.trim()) {
        showInputError(input, 'This field is required');
        return false;
    }
    
    // Check for email format
    if (input.type === 'email' && input.value.trim()) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input.value)) {
            showInputError(input, 'Please enter a valid email address');
            return false;
        }
    }
    
    // Check numeric inputs
    if ((input.type === 'number' || input.hasAttribute('data-type-number')) && input.value.trim()) {
        const value = parseFloat(input.value);
        
        if (isNaN(value)) {
            showInputError(input, 'Please enter a valid number');
            return false;
        }
        
        if (input.hasAttribute('min') && value < parseFloat(input.getAttribute('min'))) {
            showInputError(input, `Value cannot be less than ${input.getAttribute('min')}`);
            return false;
        }
        
        if (input.hasAttribute('max') && value > parseFloat(input.getAttribute('max'))) {
            showInputError(input, `Value cannot be greater than ${input.getAttribute('max')}`);
            return false;
        }
    }
    
    // Check password strength if data-password-validate is present
    if (input.type === 'password' && input.hasAttribute('data-password-validate') && input.value.trim()) {
        if (input.value.length < 8) {
            showInputError(input, 'Password must be at least 8 characters long');
            return false;
        }
    }
    
    // Check for custom pattern
    if (input.pattern && input.value.trim()) {
        const pattern = new RegExp(input.pattern);
        if (!pattern.test(input.value)) {
            const errorMsg = input.getAttribute('data-error-pattern') || 'Please match the requested format';
            showInputError(input, errorMsg);
            return false;
        }
    }
    
    return true;
}

/**
 * Show error message for input
 */
function showInputError(input, message) {
    // Clear any existing errors
    clearInputError(input);
    
    // Add error class to input
    input.classList.add('is-invalid');
    
    // Create error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'invalid-feedback';
    errorElement.textContent = message;
    
    // Add error message after input
    input.parentNode.appendChild(errorElement);
}

/**
 * Clear error message for input
 */
function clearInputError(input) {
    // Remove error class
    input.classList.remove('is-invalid');
    
    // Remove error message
    const errorElement = input.parentNode.querySelector('.invalid-feedback');
    if (errorElement) {
        errorElement.remove();
    }
}

/**
 * Validate entire form
 */
function validateForm(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });
    
    // Check if passwords match if confirm password field exists
    const password = form.querySelector('input[name="password"]');
    const confirmPassword = form.querySelector('input[name="password_confirm"]');
    
    if (password && confirmPassword && password.value !== confirmPassword.value) {
        showInputError(confirmPassword, 'Passwords do not match');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Show an alert message
 */
function showAlert(type, message) {
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} fade-in`;
    alertElement.role = 'alert';
    alertElement.textContent = message;
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'close';
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', function() {
        alertElement.remove();
    });
    
    alertElement.appendChild(closeButton);
    
    // Find alert container or create one
    let alertContainer = document.querySelector('.alert-container');
    
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container';
        document.body.appendChild(alertContainer);
    }
    
    // Add alert to container
    alertContainer.appendChild(alertElement);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertElement.style.opacity = '0';
        setTimeout(() => {
            alertElement.remove();
            
            // Remove container if empty
            if (alertContainer.children.length === 0) {
                alertContainer.remove();
            }
        }, 300);
    }, 5000);
}

/**
 * Format number as currency
 */
function formatCurrency(number) {
    // Convert string to number if needed
    const num = typeof number === 'string' ? parseFloat(number) : number;
    
    // Check if the number is valid
    if (isNaN(num)) return '0.00';
    
    // Format as number with 2 decimal places
    return num.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

/**
 * Get CSRF token from cookies
 */
function getCsrfToken() {
    const name = 'csrftoken';
    const cookieValue = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return cookieValue ? cookieValue.pop() : '';
}
