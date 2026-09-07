// UI Helper Module for Toast Notifications and DOM Management

const UI = {
    // Show Toast Notification
    showToast: function(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        let icon = 'fa-circle-info';
        if (type === 'success') icon = 'fa-circle-check';
        if (type === 'error') icon = 'fa-triangle-exclamation';

        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    },

    // Show / Hide Element
    showElement: function(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove('hidden');
    },

    hideElement: function(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add('hidden');
    },

    // Scroll smoothly to section
    scrollTo: function(id) {
        const el = document.getElementById(id);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth' });
        }
    }
};

// Dark / Light Theme Toggle Placeholder
document.addEventListener('DOMContentLoaded', () => {
    const themeBtn = document.getElementById('btn-theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            document.body.classList.toggle('dark-theme');
            UI.showToast('Theme setting toggled', 'info');
        });
    }
});