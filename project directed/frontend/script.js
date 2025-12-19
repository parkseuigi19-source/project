import { auth } from './modules/auth.js';
import { dashboard } from './modules/dashboard.js';
import { logs } from './modules/logs.js';
import { analysis } from './modules/analysis.js';
import { settings } from './modules/settings.js';
import { ui } from './modules/ui.js';

// Global App State
window.app = {
  ...dashboard,
  logs,
  analysis,
  settings,
  auth
};

async function initApp() {
  const user = await auth.init();

  if (user) {
    showDashboard(user);
  } else {
    showTypeSelection();
  }
}

function showTypeSelection() {
  ui.show('type-selection-screen');
  ui.hide('app-main');

  // Type Card Click Handlers
  document.querySelectorAll('.type-card').forEach(card => {
    card.addEventListener('click', async () => {
      const type = card.dataset.type;
      const username = prompt('사용자 이름을 입력하세요 (예: user1):', 'user1');
      if (!username) return;

      await auth.login(username, type);
      showDashboard(auth.user);
    });
  });
}

function showDashboard(user) {
  ui.hide('type-selection-screen');
  ui.show('app-main');

  // Set User details in UI
  ui.el('user-name-display').textContent = user.username;
  ui.el('user-type-display').textContent = getUserTypeLabel(user.user_type);

  dashboard.init();
  logs.init();
  analysis.init();
  settings.init();
}

function getUserTypeLabel(type) {
  const map = {
    'student': '학생',
    'jobseeker': '취준생',
    'developer': '개발자'
  };
  return map[type] || type;
}

document.addEventListener('DOMContentLoaded', initApp);