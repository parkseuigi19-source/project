// ============================
// 안전한 Todo 렌더링
// ============================
const listEl = document.getElementById('item-list');
const inputEl = document.getElementById('item-input');

const API_URL = 'http://127.0.0.1:8000';

// HTML 이스케이프
function escapeHtml(s) {
  return s.replace(/[&<>"']/g, m => (
    {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]
  ));
}

// ============================
// Todo 리스트 렌더링
// ============================
async function render() {
  if (!listEl) return console.error("item-list 요소를 찾을 수 없습니다.");

  try {
    const response = await fetch(`${API_URL}/todos/`);
    if (!response.ok) throw new Error(`서버 오류: ${response.status}`);
    const todos = await response.json();

    if (!Array.isArray(todos)) {
      console.warn("todos가 배열이 아님:", todos);
      listEl.innerHTML = '<li>할 일이 없습니다.</li>';
      return;
    }

    listEl.innerHTML = todos.length
      ? todos.map(t => `
          <li class="todo-item ${t.done ? 'done' : ''} ${t.important ? 'important' : ''}">
            <div class="item-left">
              <input type="checkbox"
                     class="checkbox"
                     ${t.done ? 'checked' : ''}
                     title="완료"
                     onchange="toggleDone('${t.id}', this.checked)">
              <button class="star-toggle" title="중요 토글" onclick="toggleImportant('${t.id}', ${!t.important})">
                ${t.important ? '⭐' : '☆'}
              </button>
            </div>
            <span class="title">${escapeHtml(t.text)}</span>
            <div class="item-buttons">
              <button class="edit-btn" onclick="editItem('${t.id}')">수정</button>
              <button class="delete-btn" onclick="deleteItem('${t.id}')">삭제</button>
            </div>
          </li>
        `).join('')
      : '<li>할 일이 없습니다.</li>';

  } catch (e) {
    console.error(e);
    listEl.innerHTML = '<li>서버 연결 실패</li>';
  }
}

// ============================
// Todo CRUD 함수
// ============================
window.createItem = async () => {
  if (!inputEl) return;
  const text = (inputEl.value || '').trim();
  if (!text) return alert('오늘 할 일을 입력하세요.');

  try {
    const response = await fetch(`${API_URL}/todos/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    
    if (!response.ok) throw new Error('추가 실패');
    
    inputEl.value = '';
    render();
  } catch (e) {
    alert('할 일 추가 실패: ' + e.message);
  }
};

window.editItem = async (id) => {
  const newText = prompt('내용 수정');
  if (newText === null) return;
  const text = newText.trim();
  if (!text) return;
  
  try {
    const response = await fetch(`${API_URL}/todos/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    
    if (!response.ok) throw new Error('수정 실패');
    render();
  } catch (e) {
    alert('수정 실패: ' + e.message);
  }
};

window.deleteItem = async (id) => {
  if (!confirm('정말 삭제할까요?')) return;
  
  try {
    const response = await fetch(`${API_URL}/todos/${id}`, { method: 'DELETE' });
    if (!response.ok) throw new Error('삭제 실패');
    render();
  } catch (e) {
    alert('삭제 실패: ' + e.message);
  }
};

window.toggleDone = async (id, checked) => {
  try {
    await fetch(`${API_URL}/todos/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ done: checked })
    });
    render();
  } catch (e) {
    console.error('완료 상태 변경 실패:', e);
  }
};

window.toggleImportant = async (id, nextVal) => {
  try {
    await fetch(`${API_URL}/todos/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ important: nextVal })
    });
    render();
  } catch (e) {
    console.error('중요 상태 변경 실패:', e);
  }
};

// ============================
// 문제 변환: 정답 기반 빈칸형 또는 서술형
// ============================
function convertToProblem(problem) {
  const text = problem.text.trim();
  const answer = problem.answer ? problem.answer.trim() : null;
  
  // 1. 정답이 명확하고 원문에 포함된 경우 빈칸형으로 변환 시도
  if (answer && text.includes(answer) && answer.length > 1) { 
    const regex = new RegExp(`\\b${answer}\\b`, 'g');
    const blankText = text.replace(regex, '________');
    
    if (blankText !== text) {
      return {
        type: 'blank',
        text: blankText,
        answer: answer,
        original: text
      };
    }
  }

  // 2. 빈칸 처리가 어렵거나, 정답이 없는 경우 서술형/요약형으로 변환
  const questions = [
    '다음 내용에 대해 설명하시오:',
    '다음 개념을 서술하시오:',
    '다음 내용을 요약하시오:'
  ];
  const question = questions[Math.floor(Math.random() * questions.length)];
  
  const isShortOrQuestion = text.length < 50 || text.match(/[\?？:\:：]$/);
  const finalText = isShortOrQuestion ? text : question + '\n' + text;

  return {
    type: 'essay',
    text: finalText,
    answer: problem.answer || '서술형 답안',
    original: text
  };
}

// ============================
// 중요 문제 랜덤 5개 인출 (빈칸/서술형)
// ============================
window.showImportant = async () => {
  try {
    const response = await fetch(`${API_URL}/problems/important`);
    if (!response.ok) throw new Error(`서버 오류: ${response.status}`);
    const problems = await response.json();

    if (!Array.isArray(problems) || problems.length === 0) {
      listEl.innerHTML = '<li>중요 문제가 없습니다.</li>';
      return;
    }

    // 랜덤하게 최대 5개 선택
    const shuffled = [...problems].sort(() => 0.5 - Math.random());
    const randomProblems = shuffled.slice(0, Math.min(5, problems.length));
    const convertedProblems = randomProblems.map(p => convertToProblem(p));

    listEl.innerHTML = convertedProblems.map((p, idx) => {
      const answerId = `answer-${idx}`;
      return `
        <li class="problem-card ${p.type === 'blank' ? 'blank-type' : 'essay-type'}">
          <div class="qnum">${idx + 1}</div>
          <div class="problem-type-badge">${p.type === 'blank' ? '📝 빈칸 채우기' : '✏️ 서술형'}</div>
          <div class="title">${escapeHtml(p.text)}</div>
          <button class="show-answer-btn" onclick="toggleAnswer('${answerId}')">
            정답 보기
          </button>
          <div class="answer" id="${answerId}" style="display: none;">
            정답: ${escapeHtml(p.answer)}
            ${p.original ? `<br><small>원문: ${escapeHtml(p.original)}</small>` : ''}
          </div>
        </li>
      `;
    }).join('');

  } catch (e) {
    console.error(e);
    alert('중요 문제를 불러오는데 실패했습니다: ' + e.message);
  }
};

// ============================
// 정답 토글 함수
// ============================
window.toggleAnswer = (answerId) => {
  const answerDiv = document.getElementById(answerId);
  const button = answerDiv.previousElementSibling;
  
  if (answerDiv.style.display === 'none') {
    answerDiv.style.display = 'block';
    button.textContent = '정답 숨기기';
  } else {
    answerDiv.style.display = 'none';
    button.textContent = '정답 보기';
  }
};

// ============================
// 문제 파일 업로드
// ============================
window.uploadProblemDoc = async () => {
  const fileInput = document.getElementById('doc-file');
  const textInput = document.getElementById('doc-text');
  const importantCheckbox = document.getElementById('doc-important');

  if (!fileInput || !textInput || !importantCheckbox) {
    alert('페이지 로딩 오류. 새로고침 후 다시 시도하세요.');
    return;
  }

  const file = fileInput.files[0];
  const text = textInput.value?.trim();
  const importantAll = importantCheckbox.checked || false;

  // 파일 업로드
  if (file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('importantAll', importantAll ? 'true' : 'false');
    formData.append('tags', '');
    formData.append('source', file.name);

    try {
      console.log('파일 업로드 시작:', file.name, '중요:', importantAll);
      const response = await fetch(`${API_URL}/problems/upload_file`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('서버 에러:', errorText);
        throw new Error(`서버 오류: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('업로드 결과:', result);
      
      const insertedCount = result.inserted || 0;
      if (insertedCount === 0) {
        alert('⚠️ 파일에서 문제를 추출하지 못했습니다.\n파일 형식이나 내용을 확인해주세요.');
      } else {
        alert(`✅ ${insertedCount}개의 문제가 추가되었습니다!\n파일: ${file.name}\n${importantAll ? '(중요 표시됨)' : ''}`);
      }
      
      // 입력 초기화
      fileInput.value = '';
      textInput.value = '';
      importantCheckbox.checked = false;
      
    } catch (e) {
      console.error('업로드 에러:', e);
      alert('❌ 파일 업로드에 실패했습니다.\n' + e.message);
    }
    return;
  }

  // 텍스트 입력 (간단 추가)
  if (text) {
    try {
      const response = await fetch(`${API_URL}/problems/bulk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify([{
          text: text,
          important: importantAll,
          options: [],
          answer: null,
          explain: null
        }])
      });

      if (!response.ok) throw new Error(`서버 오류: ${response.status}`);
      const result = await response.json();
      console.log('텍스트 추가 결과:', result);
      
      const insertedCount = result.inserted || 0;
      if (insertedCount === 0) {
        alert('⚠️ 문제 추가에 실패했습니다.');
      } else {
        alert(`✅ ${insertedCount}개의 문제가 추가되었습니다!`);
      }
      
      // 입력 초기화
      textInput.value = '';
      importantCheckbox.checked = false;
      
    } catch (e) {
      console.error('텍스트 추가 에러:', e);
      alert('❌ 문제 추가에 실패했습니다.\n' + e.message);
    }
    return;
  }

  alert('⚠️ 파일을 선택하거나 텍스트를 입력하세요.');
};

// ============================
// 초기화
// ============================
document.addEventListener('DOMContentLoaded', () => {
  render();
  inputEl?.addEventListener('keydown', e => {
    if (e.key === 'Enter') createItem();
  });
});

// 전역 노출
window.render = render;