# 금융 사기 탐지 AI 에이전트

LangGraph + Upstage Solar + ChromaDB 기반 실시간 사기 메시지 탐지 및 분석 시스템

---

## 📌 프로젝트 개요

의심스러운 메시지(보이스피싱, 스미싱, 대출사기 등)를 입력하면 AI가 자동으로 분석하여 위험도를 평가하고 대응 방안을 제공하는 시스템입니다.

**주요 기능:**
- 사기 유형 자동 분류 (키워드 기반)
- RAG(Retrieval-Augmented Generation) 기반 유사 사례 검색
- 실시간 패턴 매칭 (scam_patterns.json)
- 웹 크롤링을 통한 최신 사기 뉴스 수집
- AI 기반 위험도 분석 (0-100점)
- 맞춤형 대응 방안 생성 (Upstage Solar LLM)

---

## 🛠️ 기술 스택

### 백엔드
- **Framework:** FastAPI 0.115.0
- **Agent Orchestration:** LangGraph 0.2.59
- **LLM:** Upstage Solar (solar-pro)
- **Embedding:** Upstage Solar Embedding (solar-embedding-1-large)
- **Vector Store:** ChromaDB 0.5.23
- **LangChain:** 0.3.12

### 프론트엔드
- **Framework:** React 18.3.1
- **Build Tool:** Vite 5.4.19
- **Language:** TypeScript 5.8.3
- **UI Components:** Radix UI + Shadcn/ui
- **Styling:** Tailwind CSS 3.4.17
- **State Management:** TanStack Query 5.83.0

### 데이터
- **공공 데이터:** 경찰청 보이스피싱 현황, 금융범죄 통계, 한국인터넷진흥원 피싱 URL
- **실시간 수집:** 네이버 뉴스 크롤링

---

## 📁 프로젝트 구조

```
frinacialRefactoring/
├── app/                         # FastAPI 앱
│   ├── main.py                  # 메인 서버 (엔트리포인트)
│   ├── config.py                # 환경 설정 (Pydantic Settings)
│   ├── schemas.py               # API 요청/응답 스키마
│   └── dependencies.py          # 의존성 주입
│
├── agent/                       # LangGraph 에이전트
│   ├── graph.py                 # 그래프 정의 (워크플로우)
│   ├── state.py                 # 에이전트 상태 정의
│   └── nodes/                   # LangGraph 노드
│       ├── classify.py          # [1/4] 사기 유형 분류
│       ├── retrieve.py          # [2/4] 유사 사례 검색 (RAG)
│       ├── analyze.py           # [3/4] 위험도 분석
│       └── generate.py          # [4/4] 대응 방안 생성 (LLM)
│
├── infrastructure/              # 인프라 레이어
│   ├── vector_store/
│   │   └── scam_repository.py   # ChromaDB 리포지토리
│   └── llm/
│       └── client.py            # Upstage LLM 클라이언트
│
├── domain/                       # Domain Layer
│   └── scam_detection/
│       └── models.py             # 도메인 모델 정의
│
├── scripts/                     # 유틸리티 스크립트
│   ├── web_crawler.py           # 웹 크롤러 (네이버 뉴스)
│   ├── update_vectorstore_with_web.py  # 벡터스토어 업데이트
│   ├── auto_crawl_and_analyze.py       # 자동 크롤링 + 분석
│   └── test_graph.py            # 그래프 테스트
│
├── data/                        # 데이터 저장소
│   ├── chroma_scam_defense/     # ChromaDB 영구 저장소
│   │   ├── scam_patterns.json   # 사기 패턴 DB
│   │   └── scam_knowledge_base.json  # 지식 베이스
│   ├── analysis_results/        # 분석 결과 저장
│   └── *.csv                    # 공공 데이터셋
│
├── frontend/                    # React 프론트엔드
│   ├── src/
│   │   ├── App.tsx              # 메인 앱
│   │   ├── pages/
│   │   │   └── Index.tsx        # 메인 페이지
│   │   └── components/
│   │       ├── MessageForm.tsx  # 메시지 입력 폼
│   │       ├── AnalysisCard.tsx # 분석 결과 카드
│   │       ├── RiskBadge.tsx    # 위험도 배지
│   │       └── RiskScoreBar.tsx # 위험도 점수 바
│   ├── package.json
│   └── vite.config.ts
│
├── .env                         # 환경 변수
└── requirements.txt             # Python 의존성
```

---

## 🚀 실행 방법

### 1. 백엔드 실행

#### 1-1. Python 가상환경 생성
```bash
python -m venv .venv
```

#### 1-2. 가상환경 활성화
**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

#### 1-3. 의존성 설치
```bash
pip install -r requirements.txt
```

#### 1-4. 환경 변수 설정
`.env` 파일을 프로젝트 루트에 생성하고 다음 내용을 입력:

```env
# 필수: Upstage API Key
UPSTAGE_API_KEY=your_upstage_api_key_here

# 선택: LangSmith (추적용)
LANGCHAIN_TRACING_V2=True
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=scam-detection

# 선택: 서버 설정
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
```

#### 1-5. ChromaDB 벡터스토어 초기화 (최초 1회)
```bash
python scripts/update_vectorstore_with_web.py
```

#### 1-6. 서버 실행
```bash
python app/main.py
```

또는

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**서버 확인:**
- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health

---

### 2. 프론트엔드 실행

#### 2-1. 디렉토리 이동
```bash
cd frontend
```

#### 2-2. 의존성 설치
```bash
npm install
```

#### 2-3. 개발 서버 실행
```bash
npm run dev
```

**프론트엔드 접속:**
- http://localhost:8080/ (기본 포트)

#### 2-4. 프로덕션 빌드
```bash
npm run build
```

---

## 🔑 환경 변수

### 백엔드 (.env)

| 변수명 | 필수 | 설명 | 기본값 | 예시 |
|--------|------|------|--------|------|
| `UPSTAGE_API_KEY` | ✅ | Upstage API 키 | - | `up_xxxxx...` |
| `LANGCHAIN_TRACING_V2` | ❌ | LangSmith 추적 활성화 | `False` | `True` |
| `LANGCHAIN_API_KEY` | ❌ | LangSmith API 키 | - | `lsv2_pt_...` |
| `LANGCHAIN_PROJECT` | ❌ | LangSmith 프로젝트명 | `scam-detection` | `my-project` |
| `DEBUG` | ❌ | 디버그 모드 | `False` | `True` |
| `API_HOST` | ❌ | API 호스트 | `0.0.0.0` | `127.0.0.1` |
| `API_PORT` | ❌ | API 포트 | `8000` | `9000` |
| `LLM_MODEL` | ❌ | LLM 모델명 | `solar-pro` | `solar-mini` |
| `LLM_TEMPERATURE` | ❌ | LLM Temperature | `0.1` | `0.5` |
| `LLM_MAX_TOKENS` | ❌ | LLM 최대 토큰 | `2000` | `3000` |
| `CHROMA_PATH` | ❌ | ChromaDB 경로 | `data/chroma_scam_defense` | `./chroma` |

### 프론트엔드 (frontend/.env)

| 변수명 | 필수 | 설명 | 예시 |
|--------|------|------|------|
| `VITE_SUPABASE_URL` | ❌ | Supabase URL (미사용) | - |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | ❌ | Supabase Key (미사용) | - |

---

## 🔗 주요 API 엔드포인트

### 1. 루트 엔드포인트
```http
GET /
```

**응답 예시:**
```json
{
  "service": "Scam Detection Agent",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "docs": "/docs",
    "health": "/health",
    "detect": "/api/v1/detect"
  },
  "langsmith_enabled": true,
  "upstage_configured": true
}
```

---

### 2. 헬스체크
```http
GET /health
```

**응답 예시:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-02-13T12:00:00",
  "graph_loaded": true,
  "upstage_configured": true,
  "langsmith_enabled": true
}
```

---

### 3. 사기 탐지 (메인 API)
```http
POST /api/v1/detect
```

**요청 (Request):**
```json
{
  "message": "금융감독원입니다. 귀하의 계좌가 범죄에 연루되어 안전계좌로 이체해야 합니다.",
  "sender": "02-1234-5678"
}
```

**응답 (Response):**
```json
{
  "success": true,
  "is_scam": true,
  "scam_type": "보이스피싱",
  "confidence": 0.9,
  "risk_level": "매우높음",
  "risk_score": 95,
  "risk_factors": [
    "'보이스피싱' 패턴 감지",
    "높은 분류 신뢰도 (90%)",
    "3개 사기 패턴 매칭",
    "'보이스피싱' 고위험 패턴 매칭"
  ],
  "analysis": "🚨 매우 위험한 보이스피싱입니다...\n\n[AI 생성 분석 내용]",
  "recommendations": "🛡️ 즉시 대응 방법:\n1. ❌ 절대 돈을 보내지 마세요...",
  "processing_time": 3.45,
  "matched_patterns_count": 3,
  "similar_cases_count": 5
}
```

**응답 필드 설명:**
- `is_scam`: 사기 여부 (Boolean)
- `scam_type`: 사기 유형 (보이스피싱, 스미싱, 대출사기, 투자사기, 메신저피싱 등)
- `confidence`: 분류 신뢰도 (0.0 ~ 1.0)
- `risk_level`: 위험도 레벨 (매우높음, 높음, 중간, 낮음, 안전)
- `risk_score`: 위험도 점수 (0 ~ 100)
- `risk_factors`: 위험 요인 리스트
- `analysis`: AI 종합 분석 내용
- `recommendations`: 대응 방안 및 신고 방법
- `processing_time`: 처리 시간 (초)
- `matched_patterns_count`: 매칭된 패턴 수
- `similar_cases_count`: 유사 사례 수

**에러 응답:**
```json
{
  "success": false,
  "error": "서버 내부 오류가 발생했습니다",
  "detail": "..."
}
```

---

## 🧩 LangGraph 워크플로우

```
START
  ↓
┌─────────────────────┐
│ classify            │  [1/4] 사기 유형 분류
│ (키워드 기반)       │  → scam_type, confidence
└─────────────────────┘
  ↓
┌─────────────────────┐
│ retrieve            │  [2/4] 유사 사례 검색
│ (RAG + 패턴 매칭)   │  → similar_cases, matched_patterns
└─────────────────────┘
  ↓
┌─────────────────────┐
│ analyze             │  [3/4] 위험도 분석
│ (점수 계산)         │  → risk_level, risk_score, risk_factors, is_scam
└─────────────────────┘
  ↓
┌─────────────────────┐
│ recommend           │  [4/4] 대응 방안 생성
│ (LLM)               │  → analysis, recommendations
└─────────────────────┘
  ↓
END
```

### 각 노드 설명

#### 1️⃣ classify (사기 유형 분류)
- **파일:** `agent/nodes/classify.py`
- **역할:** 키워드 기반으로 사기 유형을 빠르게 분류
- **출력:** `scam_type`, `confidence`
- **처리 시간:** ~0.1초 (LLM 호출 없음)

**분류 가능한 사기 유형:**
- 보이스피싱: 금융감독원, 검찰, 안전계좌 등
- 스미싱: http, 링크, 클릭, 택배 등
- 대출사기: 대출, 무담보, 선입금 등
- 투자사기: 투자, 수익률, 코인 등
- 메신저피싱: 엄마, 아빠, 카톡, 긴급 등

---

#### 2️⃣ retrieve (유사 사례 검색)
- **파일:** `agent/nodes/retrieve.py`
- **역할:** 병렬로 3가지 검색 수행
  1. **RAG 검색:** ChromaDB에서 유사 사기 사례 검색 (벡터 검색)
  2. **패턴 매칭:** `scam_patterns.json`에서 실시간 패턴 분석
  3. **웹 크롤링:** 네이버 뉴스에서 최신 사기 뉴스 수집
- **출력:** `similar_cases`, `matched_patterns`
- **처리 시간:** ~1-2초 (병렬 처리)

---

#### 3️⃣ analyze (위험도 분석)
- **파일:** `agent/nodes/analyze.py`
- **역할:** 위험도 점수 계산 및 사기 여부 판단
- **출력:** `risk_level`, `risk_score`, `risk_factors`, `is_scam`
- **처리 시간:** ~0.1초

**점수 계산 로직:**
- 사기 유형 기본 점수: 10~40점
- 분류 신뢰도 가중치: 0~20점
- 매칭된 패턴: 패턴당 10점 + 위험도별 추가 점수 (0~30점)
- 유사 사례: 3개 이상 시 10점, 5개 이상 시 15점

**위험도 레벨:**
- 매우높음: 80점 이상
- 높음: 60~79점
- 중간: 40~59점
- 낮음: 20~39점
- 안전: 0~19점

**사기 판단 기준:**
- 위험도 60점 이상 또는 위험도 레벨이 "높음" 이상

---

#### 4️⃣ recommend (대응 방안 생성)
- **파일:** `agent/nodes/generate.py`
- **역할:** Upstage Solar LLM을 사용하여 종합 분석 및 대응 방안 생성
- **출력:** `analysis`, `recommendations`
- **처리 시간:** ~2-3초 (LLM 호출)

**LLM 프롬프트 구성:**
- 의심 메시지 + 발신자
- 사기 유형 + 위험도
- 매칭된 패턴 분석
- RAG 검색 결과 (과거 유사 사례)
- 실시간 패턴 매칭 결과

**생성 내용:**
1. 사기 여부 판단 및 위험도 평가
2. 사기 유형 및 수법 설명
3. 즉시 대응 방법 (우선순위별)
4. 절대 하지 말아야 할 행동
5. 신고 방법 및 연락처
6. 예방 팁 및 주의사항

---

## 🐛 에러 해결 가이드

### 1. `UPSTAGE_API_KEY is required`
**원인:** 환경 변수에 Upstage API 키가 설정되지 않음

**해결:**
```bash
# .env 파일에 추가
UPSTAGE_API_KEY=your_actual_api_key_here
```

---

### 2. `ChromaDB 검색 실패` 또는 `컬렉션 없음`
**원인:** ChromaDB 벡터스토어가 초기화되지 않음

**해결:**
```bash
# 벡터스토어 초기화
python scripts/update_vectorstore_with_web.py
```

---

### 3. `AI 에이전트가 초기화 중입니다` (503 에러)
**원인:** 서버 시작 시 LangGraph 워크플로우 로드 실패

**해결:**
1. 서버 로그 확인
2. 환경 변수 확인 (`UPSTAGE_API_KEY`)
3. 의존성 재설치: `pip install -r requirements.txt`

---

### 4. `LLM API 타임아웃`
**원인:** Upstage API 응답 지연 또는 네트워크 문제

**해결:**
```bash
# .env에서 타임아웃 증가
LLM_TIMEOUT=30
```

---

### 5. `웹 크롤링 실패`
**원인:** 네이버 뉴스 페이지 구조 변경 또는 접근 제한

**해결:**
- 웹 크롤링 실패는 무시하고 진행됨 (RAG + 패턴 매칭만으로도 분석 가능)
- 필요 시 `scripts/web_crawler.py` 수정

---

### 6. `invoke vs ainvoke`
**LangGraph 실행 방법:**
- **비동기 (FastAPI):** `await GRAPH.ainvoke(state)` ✅
- **동기 (스크립트):** `GRAPH.invoke(state)` ✅

**주의:** FastAPI 비동기 환경에서는 반드시 `ainvoke` 사용

---

### 7. State 키 누락 에러
**원인:** `AgentState` TypedDict에 정의된 키가 누락됨

**해결:** `app/main.py`에서 초기 상태 생성 시 모든 키 포함:
```python
initial_state = {
    "message": req.message,
    "sender": req.sender,
    "scam_type": None,
    "confidence": None,
    "similar_cases": [],
    "matched_patterns": [],
    "risk_level": None,
    "risk_score": None,
    "risk_factors": [],
    "is_scam": None,
    "analysis": None,
    "recommendations": None,
    "processing_time": None,
    "completed": False,
}
```

---

## 🧪 개발자용 테스트

### 1. curl로 API 테스트
```bash
curl -X POST "http://localhost:8000/api/v1/detect" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "금융감독원입니다. 안전계좌로 이체하세요.",
    "sender": "02-1234-5678"
  }'
```

---

### 2. Python 스크립트로 그래프 테스트
```bash
python scripts/test_graph.py
```

---

### 3. LLM 클라이언트 테스트
```bash
python infrastructure/llm/client.py
```

---

### 4. 벡터스토어 업데이트
```bash
# 웹 크롤링 + 벡터스토어 업데이트
python scripts/update_vectorstore_with_web.py

# 자동 크롤링 + 분석
python scripts/auto_crawl_and_analyze.py
```

---

### 5. 프론트엔드 테스트
```bash
cd frontend
npm run test
```

---

## ⚠️ 제한사항 및 TODO

### 현재 제한사항
1. **domain 레이어 미사용:** `domain/scam_detection/` 폴더 내 파일들이 사용되지 않음 (리팩토링 필요)
2. **웹 크롤링 의존성:** 네이버 페이지 구조 변경 시 크롤링 실패 가능
3. **ChromaDB 초기화 필요:** 최초 실행 시 반드시 `update_vectorstore_with_web.py` 실행 필요
4. **LLM 호출 비용:** Upstage API 사용량에 따라 과금
5. **키워드 기반 분류:** classify 노드가 LLM 없이 단순 키워드 매칭으로 동작 (정확도 제한적)

### TODO
- [ ] domain 레이어 통합 또는 제거
- [ ] classify 노드에 LLM 기반 분류 추가 (정확도 개선)
- [ ] 실시간 ChromaDB 자동 업데이트 (스케줄러)
- [ ] 사용자 피드백 수집 기능
- [ ] 분석 결과 히스토리 저장
- [ ] 다국어 지원
- [ ] 모바일 앱 연동

---

## 📝 참고 사항

### 데이터 출처
- 경찰청 보이스피싱 현황 (공공데이터포털)
- 경찰청 사이버 금융범죄 현황 (공공데이터포털)
- 한국인터넷진흥원 피싱사이트 URL (공공데이터포털)
- 과학기술정보통신부 스팸트랩 문자 수집 내역

### LangSmith 추적
LangSmith를 활성화하면 각 노드의 실행 과정을 시각화하여 디버깅할 수 있습니다.

```bash
# .env에 추가
LANGCHAIN_TRACING_V2=True
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=scam-detection
```

웹 인터페이스: https://smith.langchain.com

---

## 📄 라이선스

MIT