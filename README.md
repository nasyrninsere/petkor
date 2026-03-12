# 🐾 펫 트래블 RAG 챗봇 맵 웹

> 반려동물 동반여행 AI 챗봇 + 카카오 지도 + 장소 추천 카드

한국관광공사 반려동물 동반여행 Open API를 활용해,  
사용자가 자연어로 질문하면 반려동물 동반 가능한 여행지를 추천하고 지도에 표시합니다.

---

## 📁 프로젝트 구조

```
5_petkor/
├── backend/               # FastAPI (Python)
│   ├── app/
│   │   ├── core/config.py          # 환경변수 설정
│   │   ├── models/schemas.py       # Pydantic 스키마
│   │   ├── routes/
│   │   │   ├── chat.py             # POST /chat
│   │   │   └── places.py           # GET /places/search, /places/{id}
│   │   ├── services/
│   │   │   ├── tourism_api.py      # 한국관광공사 API 래퍼
│   │   │   ├── query_parser.py     # 자연어 → 구조화 파싱
│   │   │   ├── retriever.py        # 후보 검색 + 점수화
│   │   │   ├── document_builder.py # API 응답 정규화
│   │   │   ├── llm_service.py      # LLM 답변 생성
│   │   │   └── cache_service.py    # Redis/메모리 캐시
│   │   └── main.py                 # FastAPI 진입점
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/              # Next.js 15 (TypeScript)
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx                # 메인 페이지
    │   └── globals.css
    ├── components/
    │   ├── MapView.tsx             # 카카오 지도
    │   ├── ChatPanel.tsx           # 챗봇 UI
    │   ├── PlaceCard.tsx           # 장소 카드
    │   ├── PlaceList.tsx           # 카드 그리드
    │   ├── FilterBar.tsx           # 지역/키워드 필터
    │   └── PlaceDetailModal.tsx    # 장소 상세 모달
    ├── lib/
    │   ├── api.ts                  # API 클라이언트
    │   └── types.ts                # TypeScript 타입
    ├── next.config.js
    ├── package.json
    └── .env.example
```

---

## 🚀 빠른 시작

### 사전 준비

- Python 3.11+
- Node.js 18+
- 한국관광공사 API 키 (기본키 포함됨)
- 카카오 디벨로퍼스 JavaScript 앱키 ([https://developers.kakao.com](https://developers.kakao.com))
- OpenAI API 키 (선택 - 없으면 규칙 기반 응답)

---

### 1. 백엔드 실행

```powershell
cd c:\antigravity\5_petkor\backend

# 가상환경 생성
python -m venv venv
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
copy .env.example .env
# .env 파일에서 OPENAI_API_KEY 등 필요한 값 입력

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

백엔드가 실행되면:
- API 문서: [http://localhost:8000/docs](http://localhost:8000/docs)
- 헬스체크: [http://localhost:8000/health](http://localhost:8000/health)

---

### 2. 프론트엔드 실행

```powershell
cd c:\antigravity\5_petkor\frontend

# 환경변수 설정
copy .env.example .env.local
# .env.local 에서 NEXT_PUBLIC_KAKAO_MAP_APP_KEY 입력

# 패키지 설치
npm install

# 개발 서버 실행
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000) 접속

---

### 3. 동시 실행 (PowerShell 2개 창)

**터미널 1 - 백엔드:**
```powershell
cd c:\antigravity\5_petkor\backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**터미널 2 - 프론트엔드:**
```powershell
cd c:\antigravity\5_petkor\frontend
npm run dev
```

---

## 🔑 환경변수

### 백엔드 (`backend/.env`)

| 변수 | 설명 | 필수 |
|------|------|------|
| `TOUR_API_KEY` | 한국관광공사 API 인증키 | ✅ |
| `OPENAI_API_KEY` | OpenAI API 키 | ❌ (없으면 fallback) |
| `REDIS_URL` | Redis URL | ❌ (없으면 메모리 캐시) |

### 프론트엔드 (`frontend/.env.local`)

| 변수 | 설명 | 필수 |
|------|------|------|
| `NEXT_PUBLIC_API_BASE_URL` | 백엔드 주소 | ✅ |
| `NEXT_PUBLIC_KAKAO_MAP_APP_KEY` | 카카오 지도 JS 키 | ✅ |

---

## 🔧 주요 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/chat` | 자연어 질문 → 장소 추천 |
| `GET` | `/places/search` | 지역/키워드 기반 검색 |
| `GET` | `/places/{contentId}` | 장소 상세 조회 |
| `GET` | `/health` | 헬스체크 |

### POST /chat 예시

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "강릉에서 강아지랑 갈 수 있는 산책 장소 추천해줘"}'
```

---

## 🏗️ 아키텍처

```
사용자 질문
    ↓
query_parser.py  → 지역/키워드/반려동물 조건 추출
    ↓
retriever.py     → API 병렬 검색 + 점수화
    ↓
llm_service.py   → LLM 프롬프트 구성 + 답변 생성
    ↓
ChatResponse     → answer + places[] 반환
```

---

## 🔌 확장 포인트 (RAG 고도화)

코드 내 주석으로 확장 포인트가 표시되어 있습니다:

1. **벡터 DB 연동** (`retriever.py`): Pinecone, Weaviate, Chroma 등으로 의미 검색 추가
2. **LangChain 연동** (`llm_service.py`): RAGChain으로 업그레이드
3. **LLM 파서** (`query_parser.py`): 규칙 기반 → OpenAI function calling으로 교체
4. **캐시 고도화** (`cache_service.py`): Redis Cluster, TTL 세분화
5. **스트리밍 응답**: Server-Sent Events 로 실시간 타이핑 효과

---

## 🛠️ 기술 스택

| 영역 | 기술 |
|------|------|
| 프론트엔드 | Next.js 15, React 18, TypeScript |
| 스타일 | Vanilla CSS (CSS Modules) |
| 지도 | Kakao Maps JavaScript API |
| 백엔드 | FastAPI, Python 3.11 |
| HTTP | httpx (async) |
| 데이터 | 한국관광공사 Open API |
| AI | OpenAI gpt-4o-mini (선택) |
| 캐시 | Redis / 메모리 (자동 전환) |
