// Debug script for Orders page
// Copy this into browser console on http://localhost:8080

console.log('🔍 Debugging Orders page...');

// Check if user is logged in
const token = localStorage.getItem('canteen_token');
console.log('Token exists:', !!token);
console.log('Token value:', token ? token.substring(0, 20) + '...' : 'null');

// Check user context
if (window.location.pathname === '/orders') {
    // Try to access the orders API directly
    fetch('http://localhost:8000/api/orders/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        console.log('Direct API call status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Direct API call data:', data);
        console.log('Number of orders:', data.length);
    })
    .catch(error => {
        console.error('Direct API call error:', error);
    });
    
    // Check if React context is working
    setTimeout(() => {
        const ordersElements = document.querySelectorAll('[data-testid="order-item"]');
        console.log('Order elements found:', ordersElements.length);
        
        const emptyState = document.querySelector('[data-testid="empty-orders"]');
        console.log('Empty state visible:', !!emptyState);
    }, 2000);
}

console.log('🔧 Debug script loaded. Check console for results.');
