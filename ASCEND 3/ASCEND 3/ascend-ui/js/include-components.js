/**
 * Component Loader Utility
 * Dynamically loads HTML components into placeholders
 */
async function loadComponent(elementId, filePath) {
    try {
        const response = await fetch(filePath);
        if (!response.ok) throw new Error(`Failed to load ${filePath}`);
        const html = await response.text();
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = html;
        }

        // Re-initialize Lucide icons after loading component
        if (window.lucide) {
            window.lucide.createIcons();
        }

        // Highlight active link
        highlightActiveLink();

        // Populate user profile from localStorage
        updateUserProfile();

        // Update Logo Links (if navigation.js is loaded)
        if (window.updateLogoLinks) {
            window.updateLogoLinks();
        }
    } catch (error) {
        console.error('Error loading component:', error);
    }
}

async function updateUserProfile() {
    const token = localStorage.getItem('auth_token');
    const userStr = localStorage.getItem('user');

    // Initial attempt from localStorage for speed
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            applyProfileData(user.name || user.username || user.user_name);
            if (user.role) applyRoleData(user.role);
        } catch (e) {
            console.error('Error parsing user data from localStorage:', e);
        }
    }

    // Always try to fetch fresh data if token exists to ensure consistency with dashboard.html
    if (token) {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/dashboard', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.user_name) {
                    applyProfileData(data.user_name);

                    // Sync back to localStorage if possible
                    if (userStr) {
                        const user = JSON.parse(userStr);
                        user.name = data.user_name; // Use 'name' as standard for this script
                        localStorage.setItem('user', JSON.stringify(user));
                    }
                }
            }
        } catch (error) {
            console.error('Error fetching fresh profile data:', error);
        }
    }
}

function applyProfileData(name) {
    if (!name) return;

    const headerName = document.querySelector('.header-user-name');
    const headerAvatar = document.querySelector('.header-user .avatar');

    if (headerName) {
        headerName.textContent = name;
    }

    if (headerAvatar) {
        const parts = name.trim().split(' ');
        let initials = parts[0][0];
        if (parts.length > 1) {
            initials += parts[parts.length - 1][0];
        }
        headerAvatar.textContent = initials.toUpperCase();
    }
}

function applyRoleData(role) {
    const headerRole = document.querySelector('.header-user-role');
    if (headerRole) {
        headerRole.textContent = role.charAt(0).toUpperCase() + role.slice(1);
    }
}

function highlightActiveLink() {
    const currentPath = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.sidebar-nav-item, .dashboard-nav-group .sidebar-nav-item');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        } else {
            // Only remove if it's not a master template item that might have multiple states
            link.classList.remove('active');
        }
    });
}

// Automatically load components and sync profile
document.addEventListener('DOMContentLoaded', () => {
    // Initial profile sync from localStorage (instant)
    updateUserProfile();

    const sidebarPlaceholder = document.getElementById('sidebar-placeholder');
    const headerPlaceholder = document.getElementById('header-placeholder');
    const navPlaceholder = document.getElementById('navigation-placeholder');

    if (navPlaceholder) {
        const src = navPlaceholder.getAttribute('data-src') || 'dashboard-navigation.html';
        loadComponent('navigation-placeholder', src);
    }
    if (sidebarPlaceholder) {
        const src = sidebarPlaceholder.getAttribute('data-src') || 'dashboard-sidebar.html';
        loadComponent('sidebar-placeholder', src);
    }
    if (headerPlaceholder) {
        const src = headerPlaceholder.getAttribute('data-src') || 'dashboard-header.html';
        loadComponent('header-placeholder', src);
    }

    // Auto-load footer if placeholder exists
    const footerPlaceholder = document.getElementById('footer-placeholder');
    if (footerPlaceholder) {
        const src = footerPlaceholder.getAttribute('data-src') || 'dashboard-footer.html';
        loadComponent('footer-placeholder', src);
    }
});
