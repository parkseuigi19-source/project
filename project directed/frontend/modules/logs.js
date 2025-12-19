import { api } from './api.js';
import { ui } from './ui.js';
import { auth } from './auth.js';

export const logs = {
    async init() {
        if (!auth.isLoggedIn()) return;
        await this.loadLogs();
    },

    async loadLogs() {
        const listEl = ui.el('log-list');
        ui.clear(listEl);

        try {
            const logs = await api.get(`/logs/?user_id=${auth.user.id}`);
            // Show latest first
            logs.reverse().forEach(log => this.renderLog(log));
        } catch (e) {
            console.error('Failed to load logs', e);
        }
    },

    async createLog() {
        const contentInput = ui.el('log-content');
        const content = contentInput.value.trim();
        if (!content) return alert('내용을 입력하세요.');

        const typeInput = document.querySelector('input[name="log-type"]:checked');
        const logType = typeInput ? typeInput.value : 'daily';

        try {
            const log = await api.post('/logs/', {
                content: content,
                log_type: logType,
                user_id: auth.user.id
            });

            // Add to top of list
            this.renderLog(log, true);
            contentInput.value = '';
        } catch (e) {
            console.error(e);
        }
    },

    renderLog(log, prepend = false) {
        const listEl = ui.el('log-list');
        const logEl = ui.create('div', ['glass-card', 'log-item']);

        const date = new Date(log.created_at).toLocaleString('ko-KR', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });

        const typeColors = {
            'daily': 'var(--color-primary)',
            'error': 'var(--color-danger)'
        };
        const typeLabel = log.log_type === 'error' ? '🔥 에러/이슈' : '📝 회고';

        logEl.innerHTML = `
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; font-size:0.85rem; color:var(--color-text-muted);">
                <span style="color:${typeColors[log.log_type] || 'white'}; font-weight:bold;">${typeLabel}</span>
                <span>${date}</span>
            </div>
            <p style="white-space: pre-wrap; line-height: 1.5;">${log.content}</p>
        `;

        if (prepend && listEl.firstChild) {
            listEl.insertBefore(logEl, listEl.firstChild);
        } else {
            listEl.appendChild(logEl);
        }
    }
};
