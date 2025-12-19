import { api } from './api.js';
import { ui } from './ui.js';
import { auth } from './auth.js';

export const analysis = {
    async init() {
        if (!auth.isLoggedIn()) return;
        // Load data fresh when tab is clicked (can be optimized events)
        document.querySelector('button[data-target="analysis-section"]').addEventListener('click', () => {
            this.loadStats();
        });
    },

    async loadStats() {
        try {
            // Re-fetch goals to get latest todos status
            const goals = await api.get(`/goals/?user_id=${auth.user.id}`);

            // Need to fetch full goals or rely on what we have. 
            // The /goals/ endpoint returns List[Goal] which includes todos: List[Todo]
            // Let's assume the backend serializer includes them.
            // If not, we might need a separate call, but for MVP let's assume `todos` are there.

            let totalGoals = goals.length;
            let totalTodos = 0;
            let completedTodos = 0;
            let goalCompletionRates = [];

            for (const goal of goals) {
                // Fetch todos for each goal if not included (Backend dependent)
                // Assuming included based on Pydantic models
                const todos = goal.todos || [];
                const goalTotal = todos.length;
                const goalDone = todos.filter(t => t.done).length;

                totalTodos += goalTotal;
                completedTodos += goalDone;

                if (goalTotal > 0) {
                    goalCompletionRates.push((goalDone / goalTotal) * 100);
                }
            }

            const avgRate = goalCompletionRates.length > 0
                ? (goalCompletionRates.reduce((a, b) => a + b, 0) / goalCompletionRates.length)
                : 0;

            this.render({
                totalGoals,
                completedTodos,
                avgRate: Math.round(avgRate)
            }, goals);

        } catch (e) {
            console.error('Analysis load failed', e);
        }
    },

    render(stats, goals) {
        ui.el('stat-total-goals').textContent = stats.totalGoals;
        ui.el('stat-completed-todos').textContent = stats.completedTodos;
        ui.el('stat-completion-rate').textContent = `${stats.avgRate}%`;

        // Render Details list
        const detailsEl = ui.el('analysis-details');
        if (goals.length === 0) {
            detailsEl.innerHTML = '<p style="text-align:center">데이터가 없습니다.</p>';
            return;
        }

        let html = '<ul style="list-style:none; padding:0;">';
        goals.forEach(goal => {
            const todos = goal.todos || [];
            const total = todos.length;
            const done = todos.filter(t => t.done).length;
            const percent = total > 0 ? Math.round((done / total) * 100) : 0;

            html += `
                <li style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                        <strong>${goal.title}</strong>
                        <span>${percent}%</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; overflow:hidden;">
                        <div style="background: var(--color-primary); width: ${percent}%; height: 100%;"></div>
                    </div>
                </li>
            `;
        });
        html += '</ul>';
        detailsEl.innerHTML = html;
    }
};
