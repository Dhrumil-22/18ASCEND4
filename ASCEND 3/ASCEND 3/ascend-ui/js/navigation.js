// Navigation JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Role-based Navigation Logic
    const user = JSON.parse(localStorage.getItem('user'));
    const role = user ? user.role : 'student';

    // Update Dashboard Link
    const dashboardLink = document.querySelector('a[href="dashboard.html"]');
    if (dashboardLink) {
        if (role === 'admin') {
            dashboardLink.setAttribute('href', 'admin-dashboard.html');
        } else if (role === 'mentor' || role === 'alumni') {
            dashboardLink.setAttribute('href', 'mentor-dashboard.html');
        }
    }

    // Role-based Logo Redirection
    window.updateLogoLinks = function () {
        const user = JSON.parse(localStorage.getItem('user'));
        const role = user ? user.role : 'student';

        // Select logo elements
        const logos = document.querySelectorAll('.nav-logo, .sidebar-logo, .header-logo');

        logos.forEach(logo => {
            // Set cursor pointer
            logo.style.cursor = 'pointer';

            // Add click listener if not already an <a>
            if (logo.tagName !== 'A') {
                logo.onclick = () => {
                    if (role === 'admin') window.location.href = 'admin-dashboard.html';
                    else if (role === 'mentor' || role === 'alumni') window.location.href = 'mentor-dashboard.html';
                    else window.location.href = 'dashboard.html';
                };
            } else {
                // Update href for <a> tags
                if (role === 'admin') logo.setAttribute('href', 'admin-dashboard.html');
                else if (role === 'mentor' || role === 'alumni') logo.setAttribute('href', 'mentor-dashboard.html');
                else logo.setAttribute('href', 'dashboard.html');
            }
        });
    };

    window.updateLogoLinks();

    // Update Profile Link (if needed, though student-profile.html is shared but might need role-specific view later)
    // For now, student-profile.html handles display based on data, so link is fine.

    // Highlight active navigation item
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navItems = document.querySelectorAll('.sidebar-nav-item');

    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPage) {
            item.classList.add('active');
        }
    });

    // Sidebar collapse functionality (Enhanced with Event Delegation and Persistence)
    const initSidebar = () => {
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) {
            document.body.classList.add('sidebar-collapsed');
            // Initial Lucide check for collapsed state
            setTimeout(() => applyCollapsedIconStyles(), 100);
        }
    };

    const applyCollapsedIconStyles = () => {
        if (!document.body.classList.contains('sidebar-collapsed')) return;
        if (window.lucide) {
            lucide.createIcons();
            const svgs = document.querySelectorAll('.sidebar svg');
            svgs.forEach(svg => {
                svg.style.minWidth = '20px';
                svg.style.display = 'inline-flex';
                svg.style.opacity = '1';
                svg.style.visibility = 'visible';
            });
        }
    };

    // Use delegation so it works with dynamically loaded sidebars
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('#collapseBtn');
        if (btn) {
            document.body.classList.toggle('sidebar-collapsed');
            const nowCollapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', nowCollapsed);

            // Re-initialize Lucide icons after collapse animation
            setTimeout(() => {
                if (window.lucide) {
                    lucide.createIcons();
                    if (nowCollapsed) applyCollapsedIconStyles();
                }
            }, 100);
        }

        // Logout functionality
        const logoutBtn = e.target.closest('#logoutBtn');
        if (logoutBtn) {
            e.preventDefault();
            if (confirm('Are you sure you want to sign out?')) {
                localStorage.removeItem('user');
                localStorage.removeItem('auth_token');
                window.location.href = 'login.html';
            }
        }
    });

    // Expose for include-components.js if needed
    window.initializeSidebarCollapse = initSidebar;
    window.applyCollapsedIconStyles = applyCollapsedIconStyles;
    initSidebar();

    // Mobile menu toggle
    const createMobileMenuToggle = () => {
        if (window.innerWidth <= 768) {
            const toggle = document.createElement('button');
            toggle.className = 'mobile-menu-toggle';
            toggle.innerHTML = '☰';
            toggle.style.cssText = `
                position: fixed;
                top: 1rem;
                left: 1rem;
                z-index: 10000;
                background: var(--primary);
                color: white;
                border: none;
                width: 40px;
                height: 40px;
                border-radius: 0.5rem;
                font-size: 1.5rem;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
            `;

            toggle.addEventListener('click', () => {
                if (sidebar) {
                    sidebar.style.transform = sidebar.style.transform === 'translateX(0)'
                        ? 'translateX(-100%)'
                        : 'translateX(0)';
                }
            });

            document.body.appendChild(toggle);
        }
    };

    createMobileMenuToggle();
    window.addEventListener('resize', createMobileMenuToggle);

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href === '#' || !href.startsWith('#')) return;

            try {
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            } catch (err) {
                console.error('Scroll error:', err);
            }
        });
    });

    // Add active state to current page in header
    const headerLinks = document.querySelectorAll('.header a');
    headerLinks.forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.style.color = 'var(--primary)';
        }
    });

    // Unread Messages Indicator
    async function checkUnreadMessages() {
        const token = localStorage.getItem('auth_token');
        if (!token) return;

        try {
            const res = await fetch('http://127.0.0.1:5000/api/messages/unread_count', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                const msgBtns = document.querySelectorAll('button[onclick*="student-messages.html"], button[onclick*="mentor-messages.html"]');

                msgBtns.forEach(btn => {
                    // Check if dot already exists
                    let dot = btn.querySelector('.unread-dot');
                    if (data.unread_count > 0) {
                        if (!dot) {
                            dot = document.createElement('span');
                            dot.className = 'unread-dot';
                            dot.style.cssText = `
                                position: absolute;
                                top: 5px;
                                right: 5px;
                                width: 8px;
                                height: 8px;
                                background: #ff4d4f;
                                border-radius: 50%;
                                border: 2px solid var(--bg-card);
                            `;
                            btn.style.position = 'relative';
                            btn.appendChild(dot);
                        }
                    } else if (dot) {
                        dot.remove();
                    }
                });
            }
        } catch (e) { console.error("Unread check failed", e); }
    }

    // Initial check and poll every 30s
    checkUnreadMessages();
    setInterval(checkUnreadMessages, 30000);
});
