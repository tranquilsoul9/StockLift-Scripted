// Login and Registration functionality
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const loginError = document.getElementById('loginError');
    const registerError = document.getElementById('registerError');
    const registerSuccess = document.getElementById('registerSuccess');
    
    // Login form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const user_id = document.getElementById('loginUserId').value;
        const password = document.getElementById('loginPassword').value;
        const loginBtn = document.getElementById('loginBtn');
        
        // Clear previous errors
        loginError.style.display = 'none';
        loginError.textContent = '';
        
        // Disable button and show loading
        loginBtn.disabled = true;
        loginBtn.innerHTML = '<span>Logging in...</span>';
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: user_id,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Store user info in localStorage
                localStorage.setItem('shopkeeper_user', JSON.stringify({
                    user_id: data.user_id,
                    shop_name: data.shop_name,
                    email: data.email,
                    phone: data.phone,
                    location: data.location
                }));
                
                // Redirect to main dashboard with success parameter
                window.location.href = '/?login=success';
            } else {
                // Show error message
                loginError.textContent = data.error || 'Login failed. Please check your credentials.';
                loginError.style.display = 'block';
            }
        } catch (error) {
            console.error('Login error:', error);
            loginError.textContent = 'Network error. Please try again.';
            loginError.style.display = 'block';
        } finally {
            // Re-enable button
            loginBtn.disabled = false;
            loginBtn.innerHTML = '<span>Login</span>';
        }
    });
    
    // Registration form submission
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const user_id = document.getElementById('registerUserId').value;
        const shop_name = document.getElementById('registerShopName').value;
        const password = document.getElementById('registerPassword').value;
        const email = document.getElementById('registerEmail').value;
        const phone = document.getElementById('registerPhone').value;
        const location = document.getElementById('registerLocation').value;
        const registerBtn = document.getElementById('registerBtn');
        
        // Clear previous messages
        registerError.style.display = 'none';
        registerSuccess.style.display = 'none';
        registerError.textContent = '';
        registerSuccess.textContent = '';
        
        // Disable button and show loading
        registerBtn.disabled = true;
        registerBtn.innerHTML = '<span>Registering...</span>';
        
        try {
            const response = await fetch('/api/register-shopkeeper', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: user_id,
                    shop_name: shop_name,
                    password: password,
                    email: email,
                    phone: phone,
                    location: location
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Show success message
                registerSuccess.textContent = 'Registration successful! You can now login with your credentials.';
                registerSuccess.style.display = 'block';
                
                // Clear form
                registerForm.reset();
                
                // Switch to login tab after 2 seconds
                setTimeout(() => {
                    switchTab('login');
                    // Pre-fill the login form with the new credentials
                    document.getElementById('loginUserId').value = user_id;
                    document.getElementById('loginPassword').value = password;
                }, 2000);
            } else {
                // Show error message
                registerError.textContent = data.error || 'Registration failed. Please try again.';
                registerError.style.display = 'block';
            }
        } catch (error) {
            console.error('Registration error:', error);
            registerError.textContent = 'Network error. Please try again.';
            registerError.style.display = 'block';
        } finally {
            // Re-enable button
            registerBtn.disabled = false;
            registerBtn.innerHTML = '<span>Register</span>';
        }
    });
});

// Function to switch between login and registration tabs
function switchTab(tab) {
    const loginTab = document.querySelector('.auth-tab:first-child');
    const registerTab = document.querySelector('.auth-tab:last-child');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    // Clear any error/success messages
    document.getElementById('loginError').style.display = 'none';
    document.getElementById('registerError').style.display = 'none';
    document.getElementById('registerSuccess').style.display = 'none';
    
    if (tab === 'login') {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
    } else {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.classList.add('active');
        loginForm.classList.remove('active');
    }
} 