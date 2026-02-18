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
    const navLogo = document.querySelector('.nav-logo');
    if (navLogo) {
        if (role === 'admin') {
            navLogo.setAttribute('href', 'admin-dashboard.html');
        } else if (role === 'mentor' || role === 'alumni') {
            navLogo.setAttribute('href', 'mentor-dashboard.html');
        } else if (role === 'student') {
            navLogo.setAttribute('href', 'dashboard.html');
        } else {
            navLogo.setAttribute('href', 'index.html');
        }
    }

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

    // Sidebar collapse functionality
    const collapseBtn = document.getElementById('collapseBtn');
    const sidebar = document.querySelector('.sidebar');
    const mainLayout = document.querySelector('.main-layout');
    const header = document.querySelector('.header');

    if (collapseBtn) {
        collapseBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            const isCollapsed = sidebar.classList.contains('collapsed');

            // Re-initialize Lucide icons after collapse animation
            setTimeout(() => {
                if (window.lucide) {
                    lucide.createIcons();

                    // FORCE icons visible with inline styles
                    if (isCollapsed) {
                        const svgs = document.querySelectorAll('.sidebar svg');
                        svgs.forEach(svg => {
                            svg.style.minWidth = '20px';
                            svg.style.display = 'inline-flex';
                            svg.style.opacity = '1';
                            svg.style.visibility = 'visible';
                        });
                    }
                }
            }, 100);
        });
    }

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
});

// Page transition animation
window.addEventListener('beforeunload', function () {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.2s ease-out';
});

// Fade in on page load
window.addEventListener('load', function () {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.3s ease-in';
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 10);
});
