import { api } from './api.js';
import { ui } from './ui.js';

export const auth = {
    user: null,

    async init() {
        const storedUser = localStorage.getItem('flowtask_user');
        if (storedUser) {
            this.user = JSON.parse(storedUser);
            // Verify if user exists or update last login (optional)
            return this.user;
        }
        return null;
    },

    async login(username, userType) {
        // Simple login/register logic for MVP
        try {
            const user = await api.post('/users/', {
                username: username,
                user_type: userType
            });

            this.user = user;
            localStorage.setItem('flowtask_user', JSON.stringify(user));
            return user;
        } catch (e) {
            console.error('Login failed', e);
            alert('로그인/가입 실패');
            throw e;
        }
    },

    logout() {
        this.user = null;
        localStorage.removeItem('flowtask_user');
        location.reload();
    },

    isLoggedIn() {
        return !!this.user;
    }
};
