document.addEventListener('DOMContentLoaded', () => {
    const menuButton = document.getElementById('menu-toggle');
    const navLinks = document.querySelector('[data-menu]');

    if (menuButton && navLinks) {
        menuButton.addEventListener('click', () => {
            navLinks.classList.toggle('open');
            menuButton.classList.toggle('open');
        });

        // Optional: Close menu when a link is clicked (useful for single-page apps or after navigation)
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                if (navLinks.classList.contains('open')) {
                    navLinks.classList.remove('open');
                    menuButton.classList.remove('open');
                }
            });
        });
    }

    // Share Dropdown Toggle
    document.addEventListener('click', (e) => {
        if (e.target.closest('.share-toggle')) {
            const menu = e.target.closest('.share-wrapper').querySelector('.share-menu');
            menu.classList.toggle('show');
        } else if (!e.target.closest('.share-menu')) {
            document.querySelectorAll('.share-menu').forEach(m => m.classList.remove('show'));
        }
    });

    // AJAX for Likes and Comments
    const ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }

            const formData = new FormData(form);
            
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (form.classList.contains('like-form')) {
                        // Update like count and icon
                        const countSpan = form.querySelector('.count');
                        countSpan.innerText = data.count;
                        form.classList.toggle('liked', data.action === 'liked');

                        // Heart Pop Animation
                        if (data.action === 'liked') {
                            const heart = document.createElement('i');
                            heart.className = 'fas fa-heart heart-pop';
                            form.style.position = 'relative';
                            form.appendChild(heart);
                            setTimeout(() => heart.remove(), 700);
                        }
                    }
                    
                    if (form.classList.contains('comment-form')) {
                        // Dynamically append new comment
                        addCommentToUI(data);
                        // Hide the form/input as requested for professional feel
                        form.style.display = 'none';
                    }
                    
                    if (form.classList.contains('event-reg-form')) {
                        // Replace button with success message
                        form.parentElement.innerHTML = '<span class="status success">✅ Registered</span>';
                    }

                    if (form.classList.contains('pray-form')) {
                        // Update prayer count text in the parent container
                        const countLabel = form.parentElement.querySelector('.pray-count');
                        countLabel.innerText = `${data.count} prayers`;
                        submitBtn.innerText = '🙏 Prayed';
                        submitBtn.disabled = true;
                    }
                } else if (response.status === 403) {
                    window.location.href = '/login/';
                }
            } catch (err) {
                console.error('AJAX Error:', err);
            } finally {
                if (submitBtn) {
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                }
            }
        });
    });

    function showToast(message) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.innerText = message;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 400);
        }, 1000); // 2 Second duration as requested
    }

    function addCommentToUI(data) {
        const section = document.querySelector('.comments-section');
        const noComments = section.querySelector('.no-comments');
        if (noComments) noComments.remove();
        
        const div = document.createElement('div');
        div.className = 'comment-item';
        div.innerHTML = `<strong>${data.username}</strong><p>${data.text}</p><small>${data.created_at}</small>`;
        section.insertBefore(div, section.querySelector('.comment-form') || null);
    }

    // Theme toggle logic (if not already handled elsewhere)
    const themeToggle = document.querySelector('[data-theme-toggle]');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
});