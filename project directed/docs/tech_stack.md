# 기술 스택 정의서 (Tech Stack)

프로젝트 개발에 사용된 주요 기술과 라이브러리, 그리고 선정 이유를 기술합니다.

## 1. Backend

| 구분 | 기술/도구 | 선정 이유 | 비고 |
| :--- | :--- | :--- | :--- |
| **Language** | **Python 3.12** | 높은 생산성과 풍부한 라이브러리 생태계. | |
| **Framework** | **FastAPI** | 비동기 처리 지원으로 빠르며, 자동 문서화(Swagger UI)가 강력함. | `0.115.6` |
| **ORM** | **SQLAlchemy** | 파이썬의 표준적인 ORM으로, DB 교체가 용이하고 사용이 편리함. | `2.0.36` |
| **Server** | **Uvicorn** | ASGI 기반의 고성능 웹 서버 구현체. | `0.34.0` |
| **Utils** | **Pydantic** | API 요청/응답 데이터의 유효성 검사 및 설정 관리. | `2.10.3` |

## 2. Frontend

| 구분 | 기술/도구 | 선정 이유 | 비고 |
| :--- | :--- | :--- | :--- |
| **Core** | **Vanilla JS (ES6+)** | MVP 단계에서 프레임워크(React 등) 오버헤드 없이 빠른 개발 및 수정 용이. | Native Modules |
| **Markup** | **HTML5** | 시멘틱 태그 활용. | |
| **Styling** | **CSS3 (Variables)** | CSS 변수 기능을 활용하여 테마(Dark/Light) 관리 및 일관된 디자인 시스템 적용. | Flexbox/Grid |
| **Fonts** | **Google Fonts** | 'Outfit' 폰트를 사용하여 모던하고 깔끔한 타이포그래피 구현. | |

## 3. Database

| 구분 | 기술/도구 | 선정 이유 | 비고 |
| :--- | :--- | :--- | :--- |
| **RDBMS** | **SQLite** | 별도의 서버 설치가 필요 없는 파일 기반 DB로, 소규모 프로젝트 및 개발 단계에 최적. | `flowtask.db` |

## 4. Development Tools

| 구분 | 기술/도구 | 용도 |
| :--- | :--- | :--- |
| **IDE** | VS Code | 코드 편집 및 디버깅 |
| **Version Control** | Git | 소스 코드 버전 관리 |
| **Package Manager** | pip | 파이썬 패키지 관리 (`requirements.txt`) |
