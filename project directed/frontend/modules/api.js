const BASE_URL = 'http://localhost:8000';

export const api = {
    async get(endpoint) {
        const res = await fetch(`${BASE_URL}${endpoint}`);
        if (!res.ok) throw new Error(`GET ${endpoint} failed: ${res.status}`);
        return res.json();
    },

    async post(endpoint, body) {
        const res = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`POST ${endpoint} failed: ${res.status}`);
        return res.json();
    },

    async patch(endpoint, body) {
        const res = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`PATCH ${endpoint} failed: ${res.status}`);
        return res.json();
    },

    async delete(endpoint) {
        const res = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'DELETE',
        });
        if (!res.ok) throw new Error(`DELETE ${endpoint} failed: ${res.status}`);
        return res.json();
    },

    async upload(endpoint, formData) {
        const res = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        if (!res.ok) throw new Error(`UPLOAD ${endpoint} failed: ${res.status}`);
        return res.json();
    }
};
