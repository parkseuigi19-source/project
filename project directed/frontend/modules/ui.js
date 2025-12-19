export const ui = {
    el(id) {
        return document.getElementById(id);
    },

    create(tag, classes = [], text = '') {
        const el = document.createElement(tag);
        if (classes.length) el.classList.add(...classes);
        if (text) el.textContent = text;
        return el;
    },

    clear(element) {
        if (typeof element === 'string') {
            const el = this.el(element);
            if (el) el.innerHTML = '';
        } else if (element) {
            element.innerHTML = '';
        }
    },

    show(id) {
        const el = this.el(id);
        if (el) el.style.display = ''; // Restore default
    },

    hide(id) {
        const el = this.el(id);
        if (el) el.style.display = 'none';
    },

    makeActive(btnGroup, activeBtn) {
        btnGroup.forEach(btn => btn.classList.remove('active'));
        if (activeBtn) activeBtn.classList.add('active');
    }
};
