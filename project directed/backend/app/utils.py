import re
import os
import tempfile
import platform
import io
import pdfplumber

# ============================================
# PDF 정규화 및 파싱 로직
# ============================================
def normalize_pdf_text(text: str) -> str:
    text = re.sub(r'([가-힣A-Za-z])-\n([가-힣A-Za-z])', r'\1\2', text)
    text = re.sub(r'정\s*\n\s*답', '정답', text)
    text = re.sub(r'해\s*\n\s*설', '해설', text)
    text = re.sub(r'정답\s*(숨기기|보기)', '정답', text)
    text = re.sub(r'원문\s*[:：]', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def parse_problems_for_written(text: str, min_len: int = 15) -> list[dict]:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)

    probs = []
    problem_patterns = [
        r'(?:^|\n)\s*(\d{1,2}\.\d{1,2}\.?\d*)\s+',
        r'(?:^|\n)\s*[\-▶•★]?\s*(\d{1,3})\s*[\.)]\s+',
        r'(?:^|\n)\s*\[(\d{1,3})\]\s*',
        r'(?:^|\n)\s*\((\d{1,3})\)\s*',
        r'(?:^|\n)\s*(\d{1,3})\s*번\s+',
        r'(?:^|\n)\s*문제\s*(\d{1,3})\s*[:.)]?\s+',
        r'(?:^|\n)\s*[QqOo](\d{1,3})\s*[:.)]?\s+',
        r'(?:^|\n)\s*(\d{1,3})\s*[✏️)\.]\s+',
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
                parsed = parse_single_problem(content)
                if parsed['text']:
                    probs.append(parsed)
        if probs:
            return probs

    lines = text.split('\n')
    current_problem = []
    for line in lines:
        line = line.strip()
        if not line:
            if current_problem:
                joined = '\n'.join(current_problem)
                if len(joined) >= min_len:
                    parsed = parse_single_problem(joined)
                    if parsed['text']:
                        probs.append(parsed)
                current_problem = []
        else:
            current_problem.append(line)

    if current_problem:
        joined = '\n'.join(current_problem)
        if len(joined) >= min_len:
            parsed = parse_single_problem(joined)
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

def parse_single_problem(content: str, max_length: int = 500) -> dict:
    answer, explain = None, None
    options = []

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

    opt_pattern = r'(?:^|\n)\s*(?:[①-⑤]|\d+\)|\(\d+\)|[가-마][\).])\s*([^\n]+)'
    opt_matches = re.findall(opt_pattern, content)
    if 2 <= len(opt_matches) <= 5:
        options = [opt.strip() for opt in opt_matches if opt.strip()]
        content = re.sub(opt_pattern, '', content)

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
def extract_from_docx(file_bytes: bytes) -> str:
    from docx import Document
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        doc = Document(tmp_path)
        return "\n".join(p.text or "" for p in doc.paragraphs)
    finally:
        os.unlink(tmp_path)

def extract_from_doc(file_bytes: bytes) -> str:
    import mammoth
    result = mammoth.convert_to_text(file_bytes)
    return result.value or ""

def extract_from_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("cp949", errors="ignore")

def extract_from_hwp(file_bytes: bytes) -> str:
    if platform.system() != "Windows":
        raise RuntimeError("HWP 추출은 Windows에서만 지원됩니다.")
    import win32com.client as win32
    with tempfile.NamedTemporaryFile(delete=False, suffix=".hwp") as f:
        f.write(file_bytes)
        hwp_path = f.name
    txt_path = hwp_path.replace(".hwp", ".txt")
    try:
        try:
           hwp = win32.Dispatch("HWPFrame.HwpObject")
        except:
           # HWP 모듈이 없거나 실패시 에러 처리 (또는 조용히 넘어가도록 수정 가능)
           raise RuntimeError("HWP 자동화 객체 생성 실패")
           
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

def extract_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if t:
                text_parts.append(t)
    raw = "\n".join(text_parts).strip()
    return normalize_pdf_text(raw)

def extract_text_by_ext(ext: str, data: bytes) -> str:
    ext = ext.lower()
    if ext == ".docx": return extract_from_docx(data)
    if ext == ".doc":  return extract_from_doc(data)
    if ext == ".txt":  return extract_from_txt(data)
    if ext == ".hwp":  return extract_from_hwp(data)
    if ext == ".pdf":  return extract_from_pdf(data)
    raise ValueError(f"지원하지 않는 확장자: {ext}")
