// Check if user is logged in
document.addEventListener('DOMContentLoaded', () => {
    const user = localStorage.getItem('user');
    const token = localStorage.getItem('auth_token'); // Get token

    if (!user || !token) {
        // User not logged in, redirect to login page
        // Only redirect if we are not already on the login or register page
        const currentPage = window.location.pathname.split('/').pop();
        if (currentPage !== 'login.html' && currentPage !== 'register.html' && currentPage !== 'forgot-password.html' && currentPage !== 'index.html') {
            window.location.href = 'login.html';
        }
    } else {
        // User is logged in, you might want to update UI with user details here
        try {
            const userData = JSON.parse(user);
            // Example: Update username if element exists
            const userNameElements = document.querySelectorAll('.header-user-name, .page-title');
            userNameElements.forEach(el => {
                if (el.classList.contains('header-user-name')) {
                    el.textContent = userData.username;
                } else if (el.classList.contains('page-title') && el.textContent.includes('Welcome back')) {
                    el.textContent = `Welcome back, ${userData.username}`;
                }
            });

            const avatarElements = document.querySelectorAll('.avatar');
            avatarElements.forEach(el => {
                if (!el.textContent && userData.username) {
                    // Simple initials
                    const initials = userData.username.substring(0, 2).toUpperCase();
                    el.textContent = initials;
                }
            });
        } catch (e) {
            console.error("Error parsing user data", e);
            localStorage.removeItem('user');
            localStorage.removeItem('auth_token');
            window.location.href = 'login.html';
        }
    }
});

// Helper function to perform authenticated fetch
window.authFetch = async (url, options = {}) => {
    const token = localStorage.getItem('auth_token');

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers: headers
    });

    if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('user');
        localStorage.removeItem('auth_token');
        window.location.href = 'login.html';
    }

    return response;
};

// Handle Sign Out
const signOutLinks = document.querySelectorAll('a[href="index.html"]'); // Assuming sign out links go to index
signOutLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        if (link.textContent.includes('Sign Out')) {
            e.preventDefault();
            localStorage.removeItem('user');
            localStorage.removeItem('auth_token');
            window.location.href = 'index.html';
        }
    });
});
