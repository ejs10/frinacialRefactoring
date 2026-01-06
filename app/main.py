"""
FastAPI 메인 서버

금융 사기 탐지 AI 에이전트 REST API
"""

import os
import time
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.schemas import (
    DetectScamRequest,
    DetectScamResponse,
    ErrorResponse,
    HealthCheckResponse
)
from app.config import settings
from agent.graph import get_graph

def setup_langsmith():
    """LangSmith 추적 활성화 (API 키가 있을 경우)"""
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = str(settings.LANGCHAIN_TRACING_V2).lower()
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT or "scam-detection"
        
        print("✅ LangSmith 추적 활성화")
        print(f"   프로젝트: {settings.LANGCHAIN_PROJECT}")
    else:
        print("⚠️  LangSmith API key not found - tracing disabled")
        print("   Add LANGCHAIN_API_KEY to .env to enable tracing\n")


# LangSmith 초기화 (FastAPI 앱 생성 전에 실행)
setup_langsmith()

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    ## 금융 사기 탐지 AI 에이전트 API
    
    **LangGraph**와 **Upstage Solar**를 활용한 지능형 사기 탐지 시스템
    
    ### 주요 기능
    - 🔍 실시간 메시지 분석
    - 🤖 AI 기반 위험도 평가  
    - 📊 패턴 매칭 및 유사 사례 검색
    - 💡 맞춤형 대응 방안 제공
    
    ### 워크플로우
```
    입력 메시지
      ↓
    [1] 사기 유형 분류 (키워드 기반)
      ↓
    [2] 유사 사례 검색 (RAG + 패턴 매칭)
      ↓
    [3] 위험도 분석 (0-100점)
      ↓
    [4] 대응 방안 생성 (LLM)
      ↓
    최종 결과 반환
```
    
    ### 기술 스택
    - FastAPI: REST API 서버
    - LangGraph: 워크플로우 오케스트레이션
    - Upstage Solar: LLM 모델
    - ChromaDB: 벡터 데이터베이스
    """,
    version=settings.APP_VERSION,
    contact={
        "name": "사기 탐지 AI 에이전트",
        "url": "https://github.com/yourusername/scam-detection",
    },
    license_info={
        "name":"MIT",
    })

#CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """요청 검증 실패 핸들러"""
    errors = exc.errors()
    error_messages = []

    #에러반복
    for error in errors:
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "입력 데이터가 올바르지 않습니다",
            "detail": error_messages
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """일반 예외 핸들러"""
    print(f"❌ 서버 오류: {exc}")

    if settings.DEBUG:
        import traceback
        traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "서버 내부 오류가 발생했습니다",
            "detail": str(exc) if settings.DEBUG else "Internal Server Error"
        }
    )

# 런타임 초기화 (그래프 캐시)
# ============================================================================

print("\n" + "="*60)
print("🚀 금융 사기 탐지 AI 에이전트 서버 시작")
print("="*60)

print("\n[1/2] LangGraph 워크플로우 로드 중...")
try:
    GRAPH = get_graph()
    print("✅ 워크플로우 로드 완료")
except Exception as e:
    print(f"❌ 워크플로우 로드 실패: {e}")
    GRAPH = None

print(f"\n[2/2] 서버 설정")
print(f"  - 애플리케이션: {settings.APP_NAME}")
print(f"  - 버전: {settings.APP_VERSION}")
print(f"  - 호스트: {settings.API_HOST}:{settings.API_PORT}")
print(f"  - 디버그: {settings.DEBUG}")
print(f"  - LLM 모델: {settings.LLM_MODEL}")
print(f"  - LLM 온도: {settings.LLM_TEMPERATURE}")
print(f"  - ChromaDB: {settings.CHROMA_PATH}")

print("\n" + "="*60)
print("✅ 서버 준비 완료!")
print("="*60)
print(f"\n📍 API 문서: http://localhost:{settings.API_PORT}/docs")
print(f"📍 헬스체크: http://localhost:{settings.API_PORT}/health")
print(f"📍 탐지 API: http://localhost:{settings.API_PORT}/api/v1/detect\n")

router = APIRouter()

@app.get("/", tags=["System"])
def root():
    """
    루트 엔드포인트
    
    서비스 정보 및 사용 가능한 엔드포인트 목록 제공
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "금융 사기 탐지 AI 에이전트",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "detect": "/api/v1/detect"
        },
        "features": [
            "실시간 사기 메시지 분석",
            "AI 기반 위험도 평가",
            "패턴 매칭 및 유사 사례 검색",
            "맞춤형 대응 방안 제공"
        ],
        "langsmith_enabled": bool(settings.LANGCHAIN_API_KEY),
        "upstage_configured": bool(settings.UPSTAGE_API_KEY),
    }
@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["System"],
    summary="헬스 체크",
    description="서버 상태 및 구성 요소 로드 여부 확인"
)
def health():
    """
    헬스 체크 엔드포인트
    
    Returns:
        HealthCheckResponse: 서버 상태 정보
    """
    return HealthCheckResponse(
        status="healthy" if GRAPH is not None else "intializing",
        version=settings.APP_VERSION,
        timestamp=datetime.now().isoformat(),
        graph_loaded=GRAPH is not None,
        upstage_configured=bool(settings.UPSTAGE_API_KEY),
        langsmith_enabled=bool(settings.LANGCHAIN_API_KEY),
    )
@router.post(
    "/api/v1/detect",
    response_model=DetectScamResponse,
    responses={
        200: {
            "description": "분석 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "is_scam": True,
                        "scam_type": "보이스피싱",
                        "confidence": 0.9,
                        "risk_level": "매우높음",
                        "risk_score": 95,
                        "risk_factors": ["보이스피싱 패턴 감지"],
                        "analysis": "매우 위험한 보이스피싱입니다...",
                        "recommendations": "즉시 신고하세요...",
                        "processing_time": 3.45,
                        "matched_patterns_count": 3,
                        "similar_cases_count": 5
                    }
                }
            }
        },
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        422: {"model": ErrorResponse, "description": "입력 데이터 검증 실패"},
        500: {"model": ErrorResponse, "description": "서버 내부 오류"},
        503: {"model": ErrorResponse, "description": "서비스 준비 중"}
    },
    tags=["Detection"],
    summary="사기 메시지 탐지 및 분석",
    description="""
    의심스러운 메시지를 분석하여 사기 여부를 판단합니다.
    
    **분석 과정:**
    1. 사기 유형 분류 (키워드 기반)
    2. 유사 사례 검색 (ChromaDB + 패턴 매칭)
    3. 위험도 분석 (0-100점 산출)
    4. AI 대응 방안 생성 (Upstage Solar)
    
    **처리 시간:** 평균 2-5초
    """
)
async def detect_scam(req: DetectScamRequest) -> DetectScamResponse:
    """
    사기 탐지 메인 엔드포인트
    
    Args:
        req: DetectScamRequest (message, sender)
    
    Returns:
        DetectScamResponse: 분석 결과
    
    Raises:
        HTTPException: 검증 실패 또는 실행 오류
    """
    
    # 그래프 준비 확인
    if GRAPH is None:
        raise HTTPException(
            status_code=503,
            detail="AI 에이전트가 초기화 중입니다. 잠시 후 다시 시도해주세요."
        )
    
    # 초기 상태 생성
    initial_state: Dict[str, Any] = {
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
    
    # AI 실행
    start_time = time.time()
    
    try:
        print(f"\n📨 새로운 분석 요청")
        print(f"  메시지: {req.message[:50]}...")
        if req.sender:
            print(f"  발신자: {req.sender}")
        
        # LangGraph 비동기 실행
        result = await GRAPH.ainvoke(initial_state)
        
        processing_time = time.time() - start_time
        
        print(f"✅ 분석 완료 ({processing_time:.2f}초)")
        print(f"  → 사기 여부: {'예' if result.get('is_scam') else '아니오'}")
        print(f"  → 위험도: {result.get('risk_level')} ({result.get('risk_score')}점)\n")
        
        # 응답 생성
        return DetectScamResponse(
            success=True,
            is_scam=result.get("is_scam", False),
            scam_type=result.get("scam_type", "알 수 없음"),
            confidence=result.get("confidence", 0.5),
            risk_level=result.get("risk_level", "알 수 없음"),
            risk_score=result.get("risk_score", 0),
            risk_factors=result.get("risk_factors", []),
            analysis=result.get("analysis", "분석 결과 없음"),
            recommendations=result.get("recommendations", "대응 방안 없음"),
            processing_time=round(processing_time, 2),
            matched_patterns_count=len(result.get("matched_patterns", [])),
            similar_cases_count=len(result.get("similar_cases", [])),
        )
        
    except ValueError as e:
        print(f"❌ 입력 검증 실패: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        
        if settings.DEBUG:
            import traceback
            traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"분석 중 오류가 발생했습니다: {str(e)}" if settings.DEBUG else "분석 중 오류가 발생했습니다."
        )

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
