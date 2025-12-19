# FlowTask 🌊

**FlowTask**는 나만의 성장 방식에 맞춘 개인화된 생산성 플랫폼입니다.  
학생, 취준생, 개발자 등 각자의 페르소나에 맞춰 최적화된 목표 관리와 회고 기능을 제공합니다.

![FlowTask License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Status](https://img.shields.io/badge/status-MVP-orange)

---

## 🚀 프로젝트 소개

기존의 딱딱한 To-Do 리스트에서 벗어나, 사용자가 스스로의 맥락(Context)을 설정하고 몰입할 수 있도록 돕습니다.
파스텔 톤의 감성적인 **Glassmorphism UI**와 직관적인 UX를 통해 기록하는 즐거움을 선사합니다.

### 핵심 기능
- **👥 페르소나 기반 관리**: 학생(과목), 취준생(기업), 개발자(프로젝트) 등 타입별 맞춤 UI 제공.
- **🎯 목표 및 할 일 관리**: 직관적인 대시보드에서 큰 목표와 세부 할 일을 체계적으로 관리.
- **📝 회고 및 로그**: 하루의 배움과 에러 해결 과정을 기록하는 데일리/에러 로그.
- **📊 분석 리포트**: 시각화된 데이터로 내 성장을 한눈에 확인.

---

## 🛠 기술 스택 (Tech Stack)

### Backend
- **Framework**: `FastAPI` (Python)
- **Database**: `SQLite` (with SQLAlchemy ORM)
- **Validations**: `Pydantic`

### Frontend
- **Languages**: HTML5, CSS3, Vanilla JavaScript (ES6+ Modules)
- **Style**: Custom CSS Variables (Light/Pastel Theme), Glassmorphism Design
- **No Bundler**: 브라우저 Native Module 시스템 활용

---

## 📂 디렉토리 구조 (Directory Structure)

```bash
FlowTask/
├── backend/                # 백엔드 소스 코드
│   ├── app/
│   │   ├── routers/        # API 엔드포인트 (goals, logs, users...)
│   │   ├── models.py       # DB 모델 (SQLAlchemy)
│   │   ├── schemas.py      # Pydantic 데이터 스키마
│   │   └── database.py     # DB 연결 설정
│   └── main.py             # 앱 진입점 (FastAPI App & Static Mount)
│
├── frontend/               # 프론트엔드 소스 코드
│   ├── modules/            # JS 기능 모듈 (api, auth, dashboard...)
│   ├── index.html          # 메인 페이지
│   ├── script.js           # JS 진입점
│   └── style.css           # 전체 스타일 (CSS Variables)
│
├── docs/                   # 프로젝트 문서
│   ├── project_definition.md
│   ├── mvp_features.md
│   └── ...
│
├── flowtask.db             # SQLite 데이터베이스 (자동 생성)
├── requirements.txt        # 파이썬 의존성 목록
└── README.md               # 프로젝트 설명서
```

---

## 🏁 시작 가이드 (Getting Started)

### 1. 프로젝트 클론 (Clone)
```bash
git clone https://github.com/your-repo/flowtask.git
cd flowtask
```

### 2. 가상환경 설정 (권장)
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 서버 실행
프로젝트 루트 경로에서 아래 명령어를 실행합니다.
```bash
uvicorn backend.main:app --reload
```
또는
```bash
python backend/main.py
```

### 5. 접속
웹 브라우저를 열고 다음 주소로 접속하세요.
- **URL**: `http://localhost:8000`

---

## 📚 문서 (Documentation)
더 자세한 내용은 `docs/` 폴더 내 문서를 참고하세요.
- [프로젝트 정의서](docs/project_definition.md)
- [MVP 기능 정의서](docs/mvp_features.md)
- [시스템 아키텍처](docs/system_architecture.md)
- [기술 스택 정의서](docs/tech_stack.md)

---

## 🤝 기여 (Contributing)
1. Fork Project
2. Create Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**FlowTask** &copy; 2025 All Rights Reserved.
