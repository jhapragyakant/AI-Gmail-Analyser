/**
 * UI Utility Service
 */
const ui = {
    /**
     * Show a notification toast
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} fade-in`;
        toast.style.cssText = `
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            padding: 1rem 2rem;
            background: var(--surface-color);
            border-left: 4px solid var(--primary-color);
            border-radius: 8px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
            z-index: 1000;
            color: white;
            display: flex;
            align-items: center;
            gap: 10px;
        `;
        
        if (type === 'success') toast.style.borderLeftColor = 'var(--success)';
        if (type === 'error') toast.style.borderLeftColor = 'var(--danger)';
        if (type === 'warning') toast.style.borderLeftColor = 'var(--warning)';

        toast.innerHTML = `<span>${message}</span>`;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            toast.style.transition = 'all 0.4s ease';
            setTimeout(() => toast.remove(), 400);
        }, 4000);
    },

    /**
     * Show loading spinner in a container
     */
    showLoading(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = `
            <div class="loading-spinner" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem;">
                <div class="spinner" style="width: 40px; height: 40px; border: 4px solid rgba(255,255,255,0.1); border-top-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <p style="margin-top: 1rem; color: var(--text-secondary);">Loading...</p>
            </div>
            <style>
                @keyframes spin { to { transform: rotate(360deg); } }
            </style>
        `;
    },

    /**
     * Clear loading spinner
     */
    clearLoading(containerId, htmlContent) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = htmlContent;
        }
    }
};
