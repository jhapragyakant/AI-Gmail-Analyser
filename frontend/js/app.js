/**
 * Main Application Controller
 */
const app = {
    currentView: 'dashboard',
    user: null,

    init() {
        console.log('Initializing AI Gmail Analyser...');
        this.bindEvents();
        this.checkAuth();
        this.handleRouting();
    },

    bindEvents() {
        // Sidebar navigation
        document.querySelectorAll('.nav-item[data-view]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const view = item.getAttribute('data-view');
                this.navigateTo(view);
            });
        });

        // Logout
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                try {
                    await api.logout();
                    window.location.href = '/auth/login';
                } catch (err) {
                    ui.showToast('Logout failed', 'error');
                }
            });
        }
    },

    async checkAuth() {
        try {
            const status = await api.checkAuthStatus();
            if (status.authenticated) {
                this.user = status.user;
                document.getElementById('user-name').textContent = this.user.name || 'User';
                this.handleRouting(); // Refresh view now that we have user
            } else {
                this.renderLogin();
            }
        } catch (err) {
            console.error('Auth check failed', err);
            this.renderLogin();
        }
    },

    renderLogin() {
        const container = document.getElementById('view-container');
        container.innerHTML = `
            <div class="card" style="max-width: 450px; margin: 4rem auto; text-align: center;">
                <div class="logo-icon" style="width: 64px; height: 64px; margin: 0 auto 1.5rem; font-size: 1.5rem;">A</div>
                <h2>Welcome to Gmail Analyser</h2>
                <p style="color: var(--text-secondary); margin: 1rem 0 2rem;">
                    Sign in with your Google account to start organizing your inbox with AI.
                </p>
                <a href="/auth/login" class="btn btn-primary" style="width: 100%; padding: 1rem;">
                    <i data-lucide="log-in"></i> Sign in with Google
                </a>
            </div>
        `;
        document.getElementById('sidebar').style.display = 'none';
        document.getElementById('top-bar').style.display = 'none';
        document.getElementById('main-content').style.marginLeft = '0';
        lucide.createIcons();
    },

    navigateTo(view) {
        if (!this.user && view !== 'login') {
            this.renderLogin();
            return;
        }

        // Reset shell if coming from login
        document.getElementById('sidebar').style.display = 'flex';
        document.getElementById('top-bar').style.display = 'flex';
        document.getElementById('main-content').style.marginLeft = '';

        if (this.currentView === view && document.querySelector('.view')) {
            // Already there
        } else {
            // Update active nav state
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
                if (item.getAttribute('data-view') === view) {
                    item.classList.add('active');
                }
            });

            // Update header
            const viewTitles = {
                'dashboard': 'Dashboard',
                'scan': 'Scan Emails',
                'history': 'Scan History',
                'settings': 'Settings'
            };
            document.getElementById('current-view-title').textContent = viewTitles[view] || 'App';

            // Load view content
            this.loadView(view);
            this.currentView = view;
        }
        
        if (window.lucide) {
            lucide.createIcons();
        }
    },

    loadView(view) {
        const container = document.getElementById('view-container');
        container.innerHTML = ''; 
        
        const viewDiv = document.createElement('div');
        viewDiv.className = 'view fade-in';
        
        switch(view) {
            case 'dashboard':
                this.renderDashboard(viewDiv);
                break;
            case 'scan':
                this.renderScan(viewDiv);
                break;
            case 'history':
                this.renderHistory(viewDiv);
                break;
            case 'settings':
                this.renderSettings(viewDiv);
                break;
            default:
                viewDiv.innerHTML = '<h2>Page not found</h2>';
        }
        
        container.appendChild(viewDiv);
    },

    renderDashboard(container) {
        container.innerHTML = `
            <div class="card">
                <h2>Hello, ${this.user.name}!</h2>
                <p style="color: var(--text-secondary); margin-top: 1rem;">
                    Ready to clean up your inbox?
                </p>
                <div style="margin-top: 2rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
                    <div class="card" style="background: rgba(99, 102, 241, 0.1); border-color: var(--primary-color);">
                        <i data-lucide="zap" style="color: var(--primary-color);"></i>
                        <h3 style="margin-top: 1rem;">New Scan</h3>
                        <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0.5rem 0 1.5rem;">Analyze your unread emails now.</p>
                        <button class="btn btn-primary" onclick="app.navigateTo('scan')">Start</button>
                    </div>
                    <div class="card">
                        <i data-lucide="clock" style="color: var(--accent-color);"></i>
                        <h3 style="margin-top: 1rem;">History</h3>
                        <p style="font-size: 0.9rem; color: var(--text-secondary); margin: 0.5rem 0 1.5rem;">View previous analysis results.</p>
                        <button class="btn btn-outline" onclick="app.navigateTo('history')">View</button>
                    </div>
                </div>
            </div>
        `;
    },

    renderScan(container) {
        container.innerHTML = `
            <div class="card">
                <h2>New Email Scan</h2>
                <p style="color: var(--text-secondary); margin-top: 0.5rem;">
                    Choose the time range to scan your inbox.
                </p>
                
                <div style="margin-top: 2rem; display: flex; flex-direction: column; gap: 1.5rem;">
                    <div class="form-group">
                        <label style="display: block; margin-bottom: 0.5rem;">Scan Range (Days)</label>
                        <select id="scan-days" class="btn btn-outline" style="width: 100%; text-align: left; padding: 0.8rem;">
                            <option value="1">Last 24 Hours</option>
                            <option value="3">Last 3 Days</option>
                            <option value="7" selected>Last 7 Days</option>
                        </select>
                    </div>
                    
                    <button id="start-scan-btn" class="btn btn-primary btn-lg" style="padding: 1rem;">
                        <i data-lucide="play-circle"></i> Run AI Analysis
                    </button>
                </div>
            </div>
            
            <div id="scan-progress-container" style="margin-top: 2rem; display: none;">
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>Analysis in Progress...</h3>
                        <div class="spinner" style="width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.1); border-top-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite;"></div>
                    </div>
                    <div style="margin-top: 1.5rem; background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; overflow: hidden;">
                        <div id="scan-progress-bar" style="width: 10%; background: var(--primary-color); height: 100%; transition: width 0.5s ease;"></div>
                    </div>
                    <p id="scan-status-text" style="margin-top: 1rem; color: var(--text-secondary); text-align: center;">
                        Initializing connection to Gmail...
                    </p>
                </div>
            </div>

            <div id="scan-results-container" style="margin-top: 2rem; display: none;">
                <!-- Results will be injected here -->
            </div>
        `;

        const startBtn = container.querySelector('#start-scan-btn');
        startBtn.addEventListener('click', () => this.handleStartScan());
    },

    async handleStartScan() {
        const days = document.getElementById('scan-days').value;
        const progressContainer = document.getElementById('scan-progress-container');
        const startBtn = document.getElementById('start-scan-btn');
        
        try {
            startBtn.disabled = true;
            startBtn.innerHTML = 'Starting...';
            progressContainer.style.display = 'block';
            
            const result = await api.startScan(parseInt(days));
            ui.showToast('Scan started!', 'info');
            
            // For now, the backend is synchronous, so we'll get results immediately
            // If it was async, we would poll. But the current backend returns scan_id after completion.
            if (result.scan_id) {
                const results = await api.getScanResults(result.scan_id);
                this.showScanResults(results);
            } else {
                ui.showToast(result.message, 'warning');
                progressContainer.style.display = 'none';
                startBtn.disabled = false;
                startBtn.innerHTML = '<i data-lucide="play-circle"></i> Run AI Analysis';
            }
        } catch (err) {
            ui.showToast(err.message, 'error');
            startBtn.disabled = false;
            startBtn.innerHTML = '<i data-lucide="play-circle"></i> Run AI Analysis';
            progressContainer.style.display = 'none';
        }
    },

    showScanResults(results) {
        const progressContainer = document.getElementById('scan-progress-container');
        const resultsContainer = document.getElementById('scan-results-container');
        
        if (progressContainer) progressContainer.style.display = 'none';
        resultsContainer.style.display = 'block';
        
        const total = results.important.length + results.needs_review.length + results.unimportant.length;
        
        resultsContainer.innerHTML = `
            <div class="fade-in">
                <div style="display: flex; gap: 1rem; margin-bottom: 2rem;">
                    <div class="card" style="flex: 1; text-align: center; border-bottom: 4px solid var(--success);">
                        <div style="font-size: 2rem; font-weight: 700;">${results.important.length}</div>
                        <div style="color: var(--text-secondary); font-size: 0.8rem;">IMPORTANT</div>
                    </div>
                    <div class="card" style="flex: 1; text-align: center; border-bottom: 4px solid var(--warning);">
                        <div style="font-size: 2rem; font-weight: 700;">${results.needs_review.length}</div>
                        <div style="color: var(--text-secondary); font-size: 0.8rem;">REVIEW</div>
                    </div>
                    <div class="card" style="flex: 1; text-align: center; border-bottom: 4px solid var(--danger);">
                        <div style="font-size: 2rem; font-weight: 700;">${results.unimportant.length}</div>
                        <div style="color: var(--text-secondary); font-size: 0.8rem;">UNIMPORTANT</div>
                    </div>
                </div>

                <div class="card" style="padding: 0; overflow: hidden;">
                    <div style="padding: 1.5rem; border-bottom: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0;">Review Results</h3>
                        <button id="cleanup-btn" class="btn btn-primary" ${results.unimportant.length === 0 ? 'disabled' : ''}>
                            <i data-lucide="trash-2"></i> Trash ${results.unimportant.length} Emails
                        </button>
                    </div>
                    
                    <div id="email-list" style="max-height: 500px; overflow-y: auto;">
                        ${this.renderEmailRows(results)}
                    </div>
                </div>
            </div>
        `;

        const cleanupBtn = resultsContainer.querySelector('#cleanup-btn');
        cleanupBtn.addEventListener('click', () => this.handleCleanup(results.scan_id));
        
        lucide.createIcons();
    },

    renderEmailRows(results) {
        const allEmails = [
            ...results.important.map(e => ({...e, type: 'important'})),
            ...results.needs_review.map(e => ({...e, type: 'review'})),
            ...results.unimportant.map(e => ({...e, type: 'unimportant'}))
        ];

        if (allEmails.length === 0) return '<p style="padding: 2rem; text-align: center; color: var(--text-secondary);">No emails found.</p>';

        return allEmails.map(email => `
            <div class="email-row" style="padding: 1rem 1.5rem; border-bottom: 1px solid var(--glass-border); display: flex; align-items: center; gap: 1rem; transition: background 0.2s;">
                <div class="type-indicator" style="width: 12px; height: 12px; border-radius: 50%; background: ${this.getTypeColor(email.type)}"></div>
                <div style="flex: 1; min-width: 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 200px;">${email.sender}</span>
                        <span style="font-size: 0.75rem; color: var(--text-secondary);">Score: ${Math.round(email.confidence_score * 100)}%</span>
                    </div>
                    <div style="font-size: 0.9rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${email.subject}</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${email.snippet}</div>
                </div>
                <div class="actions" style="display: flex; gap: 0.5rem;">
                    <button class="btn btn-outline btn-sm" style="padding: 0.4rem;" title="Mark as Important" onclick="app.handleOverride(${email.id}, 'important')">
                        <i data-lucide="star" style="width: 16px; height: 16px;"></i>
                    </button>
                    <button class="btn btn-outline btn-sm" style="padding: 0.4rem;" title="Mark as Unimportant" onclick="app.handleOverride(${email.id}, 'unimportant')">
                        <i data-lucide="trash" style="width: 16px; height: 16px;"></i>
                    </button>
                </div>
            </div>
        `).join('');
    },

    getTypeColor(type) {
        if (type === 'important') return 'var(--success)';
        if (type === 'review') return 'var(--warning)';
        return 'var(--danger)';
    },

    async handleOverride(logId, classification) {
        try {
            await api.patch(`/emails/${logId}/override`, { classification });
            ui.showToast(`Marked as ${classification}`, 'success');
            // Re-fetch scan results to update UI
            if (this.currentView === 'scan') {
                // In a real app we'd just update the local state
                ui.showToast('UI update pending...', 'info');
            }
        } catch (err) {
            ui.showToast(err.message, 'error');
        }
    },

    async handleCleanup(scanId) {
        if (!confirm('Are you sure you want to trash all unimportant emails?')) return;
        
        try {
            ui.showToast('Cleaning up...', 'info');
            const result = await api.post('/emails/cleanup', { scan_id: scanId });
            ui.showToast(result.message, 'success');
            this.navigateTo('history');
        } catch (err) {
            ui.showToast(err.message, 'error');
        }
    },

    renderHistory(container) {
        container.innerHTML = `
            <div class="card">
                <h3>Scan History</h3>
                <div id="history-list" style="margin-top: 1.5rem;">
                    <!-- History items will be loaded here -->
                </div>
            </div>
        `;
        this.loadHistory();
    },

    async loadHistory() {
        const list = document.getElementById('history-list');
        ui.showLoading('history-list');
        
        try {
            const history = await api.getHistory();
            if (history.length === 0) {
                list.innerHTML = '<p style="padding: 2rem; text-align: center; color: var(--text-secondary);">No scan history found.</p>';
                return;
            }
            
            let html = '<div style="display: flex; flex-direction: column; gap: 1rem;">';
            history.forEach(item => {
                const date = new Date(item.scanned_at).toLocaleString();
                html += `
                    <div class="card" style="background: rgba(255,255,255,0.03); padding: 1.25rem; cursor: pointer; transition: transform 0.2s, background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='rgba(255,255,255,0.03)'">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: 600; display: flex; align-items: center; gap: 0.5rem;">
                                    <i data-lucide="hash" style="width: 14px; height: 14px; color: var(--primary-color);"></i>
                                    Scan #${item.id}
                                </div>
                                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                    <i data-lucide="calendar" style="width: 12px; height: 12px; vertical-align: middle;"></i> ${date}
                                </div>
                            </div>
                            <div style="display: flex; gap: 0.75rem;">
                                <div class="badge" style="background: rgba(16, 185, 129, 0.1); color: var(--success); font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px;">${item.important_count} Imp</div>
                                <div class="badge" style="background: rgba(245, 158, 11, 0.1); color: var(--warning); font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px;">${item.needs_review_count} Rev</div>
                                <div class="badge" style="background: rgba(239, 68, 68, 0.1); color: var(--danger); font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: 4px;">${item.unimportant_count} Uni</div>
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            list.innerHTML = html;
            lucide.createIcons();
        } catch (err) {
            list.innerHTML = '<p style="padding: 2rem; text-align: center; color: var(--danger);">Failed to load history.</p>';
        }
    },

    renderSettings(container) {
        container.innerHTML = `
            <div class="card">
                <h3>Settings</h3>
                <p style="color: var(--text-secondary); margin-top: 1rem;">Configuration options for your AI Gmail Analyser.</p>
                
                <div style="margin-top: 2rem; display: flex; flex-direction: column; gap: 2rem;">
                    <div>
                        <h4 style="margin-bottom: 1rem;">Account</h4>
                        <div style="display: flex; align-items: center; gap: 1rem; background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 12px;">
                            <div class="avatar" style="width: 48px; height: 48px;"></div>
                            <div>
                                <div style="font-weight: 600;" id="settings-user-name">User</div>
                                <div style="font-size: 0.85rem; color: var(--text-secondary);">Connected via Google</div>
                            </div>
                            <button class="btn btn-outline" style="margin-left: auto;">Change</button>
                        </div>
                    </div>
                    
                    <div>
                        <h4 style="margin-bottom: 1rem;">AI Model</h4>
                        <div class="form-group">
                            <select class="btn btn-outline" style="width: 100%; text-align: left; padding: 0.8rem;">
                                <option value="gemini-1.5-flash">Gemini 1.5 Flash (Fastest)</option>
                                <option value="gemini-1.5-pro">Gemini 1.5 Pro (Most Accurate)</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        if (this.user) {
            document.getElementById('settings-user-name').textContent = this.user.name || 'User';
        }
    },

    handleRouting() {
        // Basic hash-based routing if needed, or just default to dashboard
        this.navigateTo('dashboard');
    }
};

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});
