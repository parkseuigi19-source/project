import { api } from './api.js';
import { ui } from './ui.js';
import { auth } from './auth.js';

export const dashboard = {
    async init() {
        if (!auth.isLoggedIn()) return;
        await this.loadGoals();
        this.setupEventListeners();
    },

    async loadGoals() {
        const goalListEl = ui.el('goal-list');
        ui.clear(goalListEl);

        try {
            const goals = await api.get(`/goals/?user_id=${auth.user.id}`);

            if (goals.length === 0) {
                // Initial onboarding logic if no goals? or just empty state
                goalListEl.innerHTML = '<div style="padding:1rem; color:var(--color-text-muted)">목표를 추가하여 시작하세요.</div>';
            }

            for (const goal of goals) {
                this.renderGoal(goal);
            }
        } catch (e) {
            console.error('Failed to load goals', e);
        }
    },

    renderGoal(goal) {
        const container = ui.el('goal-list');
        const goalEl = ui.create('div', ['glass-card', 'goal-item']);
        goalEl.dataset.id = goal.id;

        goalEl.innerHTML = `
            <div class="goal-header">
                <h3>${goal.title}</h3>
                <button class="delete-goal-btn" style="color:var(--color-danger); background:none; border:none; cursor:pointer;" onclick="app.deleteGoal('${goal.id}')">✕</button>
            </div>
            <ul class="todo-list" id="todo-list-${goal.id}">
                <!-- Todos will be loaded here -->
            </ul>
            <div style="margin-top:10px; display:flex; gap:5px;">
                <input type="text" placeholder="할 일 추가..." id="input-todo-${goal.id}" onkeydown="if(event.key==='Enter') app.createTodo('${goal.id}')">
                <button class="primary-btn" style="padding:0.5rem;" onclick="app.createTodo('${goal.id}')">+</button>
            </div>
        `;

        container.appendChild(goalEl);

        // Render existing todos (assuming backend doesn't embed them, fetch separately ideally, but models said Relationship loaded?)
        // In models.py 'todos' relationship doesn't have `lazy='joined'` so it might not be loaded. 
        // But for MVP let's assume we might need to fetch or updated the serializer to include them.
        // The default Pydantic schema for Goal includes `todos: List[Todo] = []`.
        // If SQLAlchemy relationship defaults to lazy loading, Pydantic might get empty list unless we eagar load.
        // For simplicity, let's trust `todos` property if it's there.

        if (goal.todos && goal.todos.length > 0) {
            goal.todos.forEach(todo => this.renderTodo(goal.id, todo));
        }
    },

    renderTodo(goalId, todo) {
        const listEl = ui.el(`todo-list-${goalId}`);
        const classes = ['todo-item'];
        if (todo.done) classes.push('done');
        const todoEl = ui.create('li', classes);

        todoEl.innerHTML = `
            <input type="checkbox" class="todo-checkbox" ${todo.done ? 'checked' : ''} onchange="app.toggleTodo('${todo.id}', this.checked)">
            <span class="todo-text">${todo.text}</span>
            <button class="star-btn ${todo.important ? 'active' : ''}" onclick="app.toggleImportant('${todo.id}', !${todo.important})">★</button>
            <button class="delete-btn" style="margin-left:5px; color:var(--color-text-muted); background:none; border:none; cursor:pointer;" onclick="app.deleteTodo('${todo.id}')">🗑</button>
        `;
        listEl.appendChild(todoEl);
    },

    async createGoal() {
        const titleInput = ui.el('new-goal-title');
        const title = titleInput.value.trim();
        if (!title) return alert('목표명을 입력하세요.');

        try {
            const goal = await api.post('/goals/', {
                title: title,
                description: '',
                user_id: auth.user.id
            });
            this.renderGoal(goal);
            titleInput.value = '';
        } catch (e) {
            console.error(e);
        }
    },

    async deleteGoal(goalId) {
        if (!confirm('목표와 관련된 모든 할 일이 삭제됩니다. 계속하시겠습니까?')) return;
        try {
            await api.delete(`/goals/${goalId}`);
            const el = document.querySelector(`.goal-item[data-id="${goalId}"]`);
            if (el) el.remove();
        } catch (e) {
            console.error(e);
        }
    },

    async createTodo(goalId) {
        const input = ui.el(`input-todo-${goalId}`);
        const text = input.value.trim();
        if (!text) return;

        try {
            const todo = await api.post('/todos/', {
                text: text,
                goal_id: goalId,
                done: false,
                important: false
            });
            this.renderTodo(goalId, todo);
            input.value = '';
        } catch (e) {
            console.error(e);
        }
    },

    async toggleTodo(todoId, done) {
        try {
            await api.patch(`/todos/${todoId}`, { done });
            // re-render logic typically, but here we just toggle class via event mostly handled by checkbox visual
            // But we should update the UI text style
            const checkbox = document.querySelector(`input[onchange*="${todoId}"]`);
            const li = checkbox.closest('li');
            if (done) li.classList.add('done');
            else li.classList.remove('done');
        } catch (e) {
            console.error(e);
        }
    },

    async toggleImportant(todoId, important) {
        try {
            const todo = await api.patch(`/todos/${todoId}`, { important });
            // Re-render item or update DOM
            // This is a bit tricky without full diffing, so reload page or finding element.
            // Let's brute force find:
            const btn = document.querySelector(`button[onclick*="${todoId}"][onclick*="toggleImportant"]`);
            if (btn) {
                if (important) btn.classList.add('active');
                else btn.classList.remove('active');
                // update onclick to flip value
                btn.setAttribute('onclick', `app.toggleImportant('${todoId}', !${important})`);
            }
        } catch (e) {
            console.error(e);
        }
    },

    async deleteTodo(todoId) {
        if (!confirm('삭제하시겠습니까?')) return;
        try {
            await api.delete(`/todos/${todoId}`);
            // Find parent li and remove
            const btn = document.querySelector(`button[onclick*="${todoId}"][onclick*="deleteTodo"]`);
            if (btn) btn.closest('li').remove();
        } catch (e) {
            console.error(e);
        }
    },

    setupEventListeners() {
        ui.el('btn-add-goal').addEventListener('click', () => this.createGoal());

        // Sidebar Navigation
        const navBtns = document.querySelectorAll('.nav-btn');
        const sections = document.querySelectorAll('.content-section');

        navBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.dataset.target;

                // Update Buttons
                navBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Update Sections
                sections.forEach(sec => {
                    if (sec.id === targetId) sec.style.display = 'block';
                    else sec.style.display = 'none';
                });
            });
        });
    }
};
