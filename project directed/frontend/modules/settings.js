import { api } from './api.js';
import { ui } from './ui.js';
import { auth } from './auth.js';

export const settings = {
    init() {
        if (!auth.isLoggedIn()) return;

        // Bind UI
        document.querySelector('button[data-target="settings-section"]').addEventListener('click', () => {
            this.loadSettings();
        });
    },

    loadSettings() {
        const user = auth.user;
        ui.el('settings-username').value = user.username;

        // Select current type
        const radios = document.querySelectorAll('input[name="settings-type"]');
        radios.forEach(r => {
            if (r.value === user.user_type) r.checked = true;
        });
    },

    async updateUserType() {
        const selected = document.querySelector('input[name="settings-type"]:checked');
        if (!selected) return;

        const newType = selected.value;
        if (newType === auth.user.user_type) {
            alert('변경된 내용이 없습니다.');
            return;
        }

        try {
            // Re-use login/create endpoint which updates type if username exists
            // Or ideally use a PATCH endpoint. 
            // routers/users.py: create_user checks if exists and updates type.
            const updatedUser = await api.post('/users/', {
                username: auth.user.username,
                user_type: newType
            });

            auth.user = updatedUser;
            localStorage.setItem('flowtask_user', JSON.stringify(updatedUser));

            // Update UI
            ui.el('user-type-display').textContent = this.getUserTypeLabel(newType);
            alert('저장되었습니다.');
        } catch (e) {
            console.error('Update failed', e);
            alert('저장 실패');
        }
    },

    getUserTypeLabel(type) {
        const map = {
            'student': '학생',
            'jobseeker': '취준생',
            'developer': '개발자'
        };
        return map[type] || type;
    }
};
