// Shopkeeper Dashboard JavaScript
let currentUserId = null;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in
    const currentUser = localStorage.getItem('shopkeeper_user');
    if (!currentUser) {
        window.location.href = '/login';
        return;
    }
    
    try {
        const userData = JSON.parse(currentUser);
        currentUserId = userData.user_id;
        
        // Update header with shop name
        const shopName = userData.shop_name || 'Shopkeeper';
        document.querySelector('.shopkeeper-header h1').innerHTML = `<i class="fas fa-store"></i> ${shopName} Dashboard`;
        
        // Load all dashboard data
        loadShopkeeperStats();
        loadProducts();
        loadHistory();
        
        // Form event listeners
        document.getElementById('addProductForm').addEventListener('submit', handleAddProduct);
        document.getElementById('recordEventForm').addEventListener('submit', handleRecordEvent);
        
        // Show welcome message
        showAlert(`Welcome back, ${shopName}! Your dashboard is ready.`, 'success');
        
    } catch (error) {
        console.error('Error parsing user data:', error);
        window.location.href = '/login';
    }
});

// Tab functionality
function showTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => button.classList.remove('active'));
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// Load shopkeeper statistics
async function loadShopkeeperStats() {
    try {
        const response = await fetch(`/api/shopkeeper-stats/${currentUserId}`);
        const stats = await response.json();
        
        document.getElementById('totalProducts').textContent = stats.total_products || 0;
        document.getElementById('totalSalesValue').textContent = `₹${(stats.total_sales_value || 0).toLocaleString()}`;
        document.getElementById('totalItemsSold').textContent = stats.total_items_sold || 0;
        document.getElementById('currentInventory').textContent = stats.current_inventory_count || 0;
    } catch (error) {
        console.error('Error loading shopkeeper stats:', error);
    }
}

// Handle add product form submission
async function handleAddProduct(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const productData = {
        user_id: currentUserId,
        sku: formData.get('sku'),
        product_name: formData.get('product_name'),
        category: formData.get('category'),
        initial_quantity: parseInt(formData.get('initial_quantity'))
    };
    
    try {
        const response = await fetch('/api/add-product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('Product added successfully!', 'success');
            event.target.reset();
            loadProducts();
            loadShopkeeperStats();
        } else {
            showAlert(result.error || 'Failed to add product', 'error');
        }
    } catch (error) {
        console.error('Error adding product:', error);
        showAlert('Error adding product. Please try again.', 'error');
    }
}

// Handle record event form submission
async function handleRecordEvent(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const eventData = {
        user_id: currentUserId,
        sku: formData.get('sku'),
        event_type: formData.get('event_type'),
        quantity_changed: parseInt(formData.get('quantity_changed')),
        price_per_unit: formData.get('price_per_unit') ? parseFloat(formData.get('price_per_unit')) : null,
        notes: formData.get('notes')
    };
    
    try {
        const response = await fetch('/api/record-sale-event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(eventData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(`${eventData.event_type} recorded successfully! New quantity: ${result.new_quantity}`, 'success');
            event.target.reset();
            loadProducts();
            loadHistory();
            loadShopkeeperStats();
        } else {
            showAlert(result.error || 'Failed to record event', 'error');
        }
    } catch (error) {
        console.error('Error recording event:', error);
        showAlert('Error recording event. Please try again.', 'error');
    }
}

// Load shopkeeper products
async function loadProducts() {
    try {
        const response = await fetch(`/api/shopkeeper-products/${currentUserId}`);
        const products = await response.json();
        
        const container = document.getElementById('productsList');
        
        if (products.length === 0) {
            container.innerHTML = '<div class="no-data">No products found. Add your first product to get started!</div>';
            return;
        }
        
        let tableHTML = `
            <table class="products-table">
                <thead>
                    <tr>
                        <th>SKU</th>
                        <th>Product Name</th>
                        <th>Category</th>
                        <th>Initial Quantity</th>
                        <th>Current Quantity</th>
                        <th>Date Added</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        products.forEach(product => {
            tableHTML += `
                <tr>
                    <td><strong>${product.sku}</strong></td>
                    <td>${product.product_name}</td>
                    <td>${product.category.replace('_', ' ').toUpperCase()}</td>
                    <td>${product.initial_quantity}</td>
                    <td>${product.current_quantity}</td>
                    <td>${formatDate(product.date_added)}</td>
                </tr>
            `;
        });
        
        tableHTML += `
                </tbody>
            </table>
        `;
        
        container.innerHTML = tableHTML;
    } catch (error) {
        console.error('Error loading products:', error);
        document.getElementById('productsList').innerHTML = '<div class="no-data">Error loading products</div>';
    }
}

// Load product history
async function loadHistory() {
    try {
        const sku = document.getElementById('filterSku').value;
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        let url = `/api/product-history/${currentUserId}`;
        const params = new URLSearchParams();
        
        if (sku) params.append('sku', sku);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        const history = await response.json();
        
        const container = document.getElementById('historyList');
        
        if (history.length === 0) {
            container.innerHTML = '<div class="no-data">No history found for the selected filters.</div>';
            return;
        }
        
        let tableHTML = `
            <table class="history-table">
                <thead>
                    <tr>
                        <th>Date/Time</th>
                        <th>SKU</th>
                        <th>Product Name</th>
                        <th>Event Type</th>
                        <th>Quantity Changed</th>
                        <th>Price per Unit</th>
                        <th>Total Amount</th>
                        <th>Remaining Quantity</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        history.forEach(event => {
            const eventTypeClass = event.event_type.replace(' ', '_');
            const quantityDisplay = event.quantity_changed > 0 ? `+${event.quantity_changed}` : event.quantity_changed;
            
            tableHTML += `
                <tr>
                    <td>${formatDateTime(event.event_date)}</td>
                    <td><strong>${event.sku}</strong></td>
                    <td>${event.product_name}</td>
                    <td><span class="event-type ${eventTypeClass}">${event.event_type.replace('_', ' ').toUpperCase()}</span></td>
                    <td>${quantityDisplay}</td>
                    <td>${event.price_per_unit ? `₹${event.price_per_unit}` : '-'}</td>
                    <td>${event.total_amount ? `₹${event.total_amount.toFixed(2)}` : '-'}</td>
                    <td>${event.remaining_quantity}</td>
                    <td>${event.notes || '-'}</td>
                </tr>
            `;
        });
        
        tableHTML += `
                </tbody>
            </table>
        `;
        
        container.innerHTML = tableHTML;
    } catch (error) {
        console.error('Error loading history:', error);
        document.getElementById('historyList').innerHTML = '<div class="no-data">Error loading history</div>';
    }
}

// Export history to CSV
async function exportHistory() {
    try {
        const sku = document.getElementById('filterSku').value;
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        
        let url = `/api/export-history/${currentUserId}`;
        const params = new URLSearchParams();
        
        if (sku) params.append('sku', sku);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        const result = await response.json();
        
        if (result.success) {
            // Create a temporary link to download the file
            const link = document.createElement('a');
            link.href = result.download_url;
            link.download = result.filename.split('/').pop();
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showAlert('History exported successfully!', 'success');
        } else {
            showAlert(result.error || 'Failed to export history', 'error');
        }
    } catch (error) {
        console.error('Error exporting history:', error);
        showAlert('Error exporting history. Please try again.', 'error');
    }
}

// Show alert message
function showAlert(message, type) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.innerHTML = message;
    
    // Insert at the top of the dashboard container
    const container = document.querySelector('.dashboard-container');
    container.insertBefore(alert, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}

// Logout function
function logout() {
    localStorage.removeItem('shopkeeper_user');
    window.location.href = '/login';
}

// Format date and time for display
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
} 