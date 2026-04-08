// Debug script to test frontend API calls
// Copy this into browser console on http://localhost:8080

async function debugLogin() {
    console.log('🧪 Testing frontend API calls...');
    
    try {
        // Test login
        console.log('1. Testing login...');
        const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: 'superadmin@admin.com',
                password: 'admin@1230'
            })
        });
        
        console.log('Login response status:', response.status);
        const data = await response.json();
        console.log('Login response data:', data);
        
        if (data.access_token) {
            localStorage.setItem('canteen_token', data.access_token);
            console.log('✅ Token saved to localStorage');
            
            // Test /me endpoint
            console.log('2. Testing /me endpoint...');
            const meResponse = await fetch('http://localhost:8000/api/auth/me', {
                headers: {
                    'Authorization': `Bearer ${data.access_token}`
                }
            });
            
            console.log('Me response status:', meResponse.status);
            const userData = await meResponse.json();
            console.log('Me response data:', userData);
            
            if (userData.role === 'SUPER_ADMIN') {
                console.log('✅ User is SUPER_ADMIN - should redirect to /admin');
            }
        }
        
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

// Test CORS
async function testCORS() {
    console.log('🌐 Testing CORS...');
    try {
        const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'OPTIONS',
            headers: {
                'Origin': 'http://localhost:8080',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        });
        
        console.log('CORS preflight status:', response.status);
        console.log('CORS headers:', {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        });
    } catch (error) {
        console.error('CORS error:', error);
    }
}

console.log('🔧 Debug functions loaded. Run debugLogin() or testCORS()');
