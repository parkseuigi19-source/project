import uuid, os, re, tempfile, platform
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ============================================
# 앱 기본 설정
# ============================================
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 데이터 모델
# ============================================
class TodoCreate(BaseModel):
    text: str
    done: bool = False
    important: bool = False

class TodoPatch(BaseModel):
    text: Optional[str] = None
    done: Optional[bool] = None
    important: Optional[bool] = None

class TodoItem(BaseModel):
    id: uuid.UUID
    text: str
    done: bool = False
    important: bool = False

class Problem(BaseModel):
    id: uuid.UUID
    text: str
    source: Optional[str] = None
    tags: List[str] = []
    important: bool = False
    created_at: datetime
    options: List[str] = []
    answer: Optional[str] = None
    explain: Optional[str] = None

# ============================================
# 인메모리 DB
# ============================================
TODOS: List[TodoItem] = []
PROBLEMS: List[Problem] = []

# ============================================
# PDF 정규화 함수
# ============================================
def _normalize_pdf_text(text: str) -> str:
    # 하이픈 줄바꿈 복원
    text = re.sub(r'([가-힣A-Za-z])-\n([가-힣A-Za-z])', r'\1\2', text)
    # "정\n답" / "해\n설" 복원
    text = re.sub(r'정\s*\n\s*답', '정답', text)
    text = re.sub(r'해\s*\n\s*설', '해설', text)
    # "정답 숨기기/보기" 제거
    text = re.sub(r'정답\s*(숨기기|보기)', '정답', text)
    # "원문:" 제거
    text = re.sub(r'원문\s*[:：]', '', text)
    # 불필요한 공백 정리
    text = re.sub(r'[ \t]+', ' ', text)
    # 3줄 이상 줄바꿈 -> 2줄
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# ============================================
# 문제 파싱 함수
# ============================================
def parse_problems_for_written(text: str, min_len: int = 15) -> list[dict]:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)

    probs = []

    problem_patterns = [
        r'(?:^|\n)\s*(\d{1,2}\.\d{1,2}\.?\d*)\s+',           # 1.2. / 2.10.2
        r'(?:^|\n)\s*[\-▶•★]?\s*(\d{1,3})\s*[\.)]\s+',      # 1. / ▶1)
        r'(?:^|\n)\s*\[(\d{1,3})\]\s*',                     # [1]
        r'(?:^|\n)\s*\((\d{1,3})\)\s*',                     # (1)
        r'(?:^|\n)\s*(\d{1,3})\s*번\s+',                     # 1번
        r'(?:^|\n)\s*문제\s*(\d{1,3})\s*[:.)]?\s+',         # 문제1
        r'(?:^|\n)\s*[QqOo](\d{1,3})\s*[:.)]?\s+',          # Q1
        r'(?:^|\n)\s*(\d{1,3})\s*[✏️)\.]\s+',               # 1✏️, 2✏️
    ]

    best_matches, best_pattern = None, None
    for pattern in problem_patterns:
        matches = list(re.finditer(pattern, text))
        if len(matches) >= 2:
            if best_matches is None or len(matches) > len(best_matches):
                best_matches, best_pattern = matches, pattern

    if best_matches:
        for i, match in enumerate(best_matches):
            start_pos = match.end()
            end_pos = best_matches[i + 1].start() if i + 1 < len(best_matches) else len(text)
            content = text[start_pos:end_pos].strip()
            if len(content) >= min_len:
                parsed = _parse_single_problem(content)
                if parsed['text']:
                    probs.append(parsed)
        if probs:
            return probs

    # 패턴 실패 시 줄바꿈 기반 처리
    lines = text.split('\n')
    current_problem = []
    for line in lines:
        line = line.strip()
        if not line:
            if current_problem:
                joined = '\n'.join(current_problem)
                if len(joined) >= min_len:
                    parsed = _parse_single_problem(joined)
                    if parsed['text']:
                        probs.append(parsed)
                current_problem = []
        else:
            current_problem.append(line)

    if current_problem:
        joined = '\n'.join(current_problem)
        if len(joined) >= min_len:
            parsed = _parse_single_problem(joined)
            if parsed['text']:
                probs.append(parsed)

    if not probs and len(text) >= min_len:
        probs.append({
            "text": text.strip()[:500],
            "options": [],
            "answer": None,
            "explain": None
        })

    return probs


def _parse_single_problem(content: str, max_length: int = 500) -> dict:
    answer, explain = None, None
    options = []

    # 정답 패턴
    answer_patterns = [
        r'(?:정답\s*(?:숨기기|보기)?)\s*[:：]?\s*(.+?)(?=\n{2,}|\n해설|$)',
        r'(?:^|\n)\s*답\s*[:：]\s*(.+?)(?=\n{2,}|\n해설|$)',
        r'\[정답\]\s*(.+?)(?=\n{2,}|\n해설|$)',
        r'정답\s*[:\-]\s*(.+?)(?=\n{2,}|\n해설|$)',
        r'→\s*(.+?)(?=\n{2,}|\n해설|$)',
    ]
    for pat in answer_patterns:
        m = re.search(pat, content, re.IGNORECASE | re.DOTALL)
        if m:
            ans = m.group(1).strip()
            if len(ans) <= 50:
                answer = ans
            content = content[:m.start()] + content[m.end():]
            break

    # 해설 패턴
    explain_patterns = [
        r'(?:해설|해답|풀이|Explanation)\s*[:：]\s*(.+?)(?=\n{2,}|\n문제|\n\d+[\.)]|\Z)',
        r'\[해설\]\s*(.+?)(?=\n{2,}|\n문제|\n\d+[\.)]|\Z)',
    ]
    for pat in explain_patterns:
        m = re.search(pat, content, re.IGNORECASE | re.DOTALL)
        if m:
            explain = m.group(1).strip()[:200]
            content = content[:m.start()] + content[m.end():]
            break

    # 객관식 선지
    opt_pattern = r'(?:^|\n)\s*(?:[①-⑤]|\d+\)|\(\d+\)|[가-마][\).])\s*([^\n]+)'
    opt_matches = re.findall(opt_pattern, content)
    if 2 <= len(opt_matches) <= 5:
        options = [opt.strip() for opt in opt_matches if opt.strip()]
        content = re.sub(opt_pattern, '', content)

    # 본문 정리
    text = re.sub(r'\s+', ' ', content).strip()
    if len(text) > max_length:
        text = text[:max_length] + '...'

    return {
        "text": text,
        "options": options,
        "answer": answer,
        "explain": explain
    }

# ============================================
# 파일 추출기
# ============================================
def _extract_from_docx(file_bytes: bytes) -> str:
    from docx import Document
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        doc = Document(tmp_path)
        return "\n".join(p.text or "" for p in doc.paragraphs)
    finally:
        os.unlink(tmp_path)

def _extract_from_doc(file_bytes: bytes) -> str:
    import mammoth
    result = mammoth.convert_to_text(file_bytes)
    return result.value or ""

def _extract_from_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("cp949", errors="ignore")

def _extract_from_hwp(file_bytes: bytes) -> str:
    if platform.system() != "Windows":
        raise RuntimeError("HWP 추출은 Windows에서만 지원됩니다.")
    import win32com.client as win32
    with tempfile.NamedTemporaryFile(delete=False, suffix=".hwp") as f:
        f.write(file_bytes)
        hwp_path = f.name
    txt_path = hwp_path.replace(".hwp", ".txt")
    try:
        hwp = win32.Dispatch("HWPFrame.HwpObject")
        hwp.Open(hwp_path)
        action = hwp.CreateAction("FileSaveAs_S")
        set_ = action.CreateSet()
        action.GetDefault(set_)
        set_.SetItem("Filename", txt_path)
        set_.SetItem("Format", "TEXT")
        action.Execute(set_)
        hwp.Quit()
        with open(txt_path, "r", encoding="utf-8", errors="ignore") as rf:
            return rf.read()
    finally:
        for p in (hwp_path, txt_path):
            try:
                if os.path.exists(p): os.unlink(p)
            except:
                pass

def _extract_from_pdf(file_bytes: bytes) -> str:
    import io, pdfplumber
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t:
                text_parts.append(t)
    raw = "\n".join(text_parts).strip()
    return _normalize_pdf_text(raw)

def _extract_text_by_ext(ext: str, data: bytes) -> str:
    ext = ext.lower()
    if ext == ".docx": return _extract_from_docx(data)
    if ext == ".doc":  return _extract_from_doc(data)
    if ext == ".txt":  return _extract_from_txt(data)
    if ext == ".hwp":  return _extract_from_hwp(data)
    if ext == ".pdf":  return _extract_from_pdf(data)
    raise HTTPException(400, f"지원하지 않는 확장자: {ext}")

# ============================================
# 라우트
# ============================================
@app.get("/health")
def health():
    return {"ok": True, "time": datetime.utcnow().isoformat()}

# ----- Todos -----
@app.get("/todos/", response_model=List[TodoItem])
def list_todos():
    return TODOS

@app.post("/todos/", response_model=TodoItem, status_code=201)
def create_todo(body: TodoCreate):
    item = TodoItem(id=uuid.uuid4(), text=body.text, done=body.done, important=body.important)
    TODOS.append(item)
    return item

@app.patch("/todos/{todo_id}", response_model=TodoItem)
def patch_todo(todo_id: uuid.UUID, body: TodoPatch):
    for i, t in enumerate(TODOS):
        if t.id == todo_id:
            updated = t.model_copy(update={
                "text": body.text if body.text is not None else t.text,
                "done": t.done if body.done is None else body.done,
                "important": t.important if body.important is None else body.important,
            })
            TODOS[i] = updated
            return updated
    raise HTTPException(404, "todo not found")

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: uuid.UUID):
    global TODOS
    before = len(TODOS)
    TODOS = [t for t in TODOS if t.id != todo_id]
    if len(TODOS) == before:
        raise HTTPException(404, "todo not found")
    return

@app.get("/todos/important", response_model=List[TodoItem])
def list_important_todos():
    return [t for t in TODOS if t.done and t.important]

# ----- Problems -----
@app.post("/problems/bulk")
def problems_bulk_insert(items: List[dict]):
    inserted = 0
    for it in items:
        PROBLEMS.append(Problem(
            id=uuid.uuid4(),
            text=(it.get("text") or "").strip(),
            source=it.get("source"),
            tags=it.get("tags", []),
            important=it.get("important", False),
            created_at=datetime.utcnow(),
            options=it.get("options", []),
            answer=it.get("answer"),
            explain=it.get("explain")
        ))
        inserted += 1
    return {"inserted": inserted}

@app.get("/problems")
def list_problems(important: Optional[bool] = None):
    data = PROBLEMS
    if important is not None:
        data = [p for p in data if p.important == important]
    return [p.model_dump() for p in sorted(data, key=lambda x: x.created_at, reverse=True)]

@app.get("/problems/important")
def list_important_problems():
    return [p.model_dump() for p in PROBLEMS if p.important]

@app.post("/problems/upload_file")
async def upload_problem_file(
    file: UploadFile = File(...),
    importantAll: bool = Form(False),
    tags: str = Form(""),
    source: str = Form(None)
):
    name = file.filename or "upload"
    _, ext = os.path.splitext(name)
    data = await file.read()

    raw_text = _extract_text_by_ext(ext, data)
    parsed = parse_problems_for_written(raw_text)
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    inserted = 0
    for obj in parsed:
        PROBLEMS.append(Problem(
            id=uuid.uuid4(),
            text=obj["text"],
            options=obj.get("options", []),
            answer=obj.get("answer"),
            explain=obj.get("explain"),
            source=source or name,
            tags=tag_list,
            important=importantAll,
            created_at=datetime.utcnow()
        ))
        inserted += 1

    # 🔎 디버깅용: 처음 3문제 콘솔에 출력
    print("\n=== 디버그: 파싱된 문제 샘플 ===")
    for idx, p in enumerate(parsed[:3]):
        print(f"[{idx+1}] 문제: {p['text'][:80]}...")
        print(f"    정답: {p.get('answer')}")
        print(f"    해설: {p.get('explain')}")
        print(f"    선지: {p.get('options')}\n")
    print("================================\n")

    return {
        "inserted": inserted,
        "ext": ext.lower(),
        "message": f"{inserted}개의 문제가 업로드되었습니다."
    }

