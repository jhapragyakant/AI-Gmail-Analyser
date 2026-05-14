/**
 * API Service for AI Gmail Analyser
 */
const API_BASE_URL = window.location.origin;

const api = {
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`);
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`GET ${endpoint} failed:`, error);
            throw error;
        }
    },

    async post(endpoint, data = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`POST ${endpoint} failed:`, error);
            throw error;
        }
    },

    async patch(endpoint, data = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`PATCH ${endpoint} failed:`, error);
            throw error;
        }
    },

    async delete(endpoint) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'DELETE'
            });
            return await this.handleResponse(response);
        } catch (error) {
            console.error(`DELETE ${endpoint} failed:`, error);
            throw error;
        }
    },

    async handleResponse(response) {
        if (response.status === 401) {
            // Unauthorized - probably needs login
            window.location.href = '/auth/login';
            return;
        }
        
        const data = await response.json();
        if (!response.ok) {
            let errorMsg = 'API request failed';
            if (data.detail) {
                if (typeof data.detail === 'string') {
                    errorMsg = data.detail;
                } else if (Array.isArray(data.detail)) {
                    errorMsg = data.detail.map(e => e.msg || JSON.stringify(e)).join(', ');
                } else {
                    errorMsg = JSON.stringify(data.detail);
                }
            } else if (data.message) {
                errorMsg = data.message;
            }
            throw new Error(errorMsg);
        }
        return data;
    },

    // Auth specific
    async checkAuthStatus() {
        return this.get('/auth/status');
    },

    async logout() {
        return this.post('/auth/logout');
    },

    // Scan specific
    async startScan(days = 7) {
        return this.post('/emails/scan', { days });
    },

    async getScanResults(scanId) {
        return this.get(`/emails/results/${scanId}`);
    },

    // History
    async getHistory() {
        return this.get('/history');
    },

    async trashEmail(logId) {
        return this.post(`/emails/${logId}/trash`);
    },

    async getSettings() {
        return this.get('/settings');
    },

    async updateSettings(data) {
        return this.patch('/settings', data);
    }
};
