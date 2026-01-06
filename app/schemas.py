"""
API 요청/응답 스키마

Pydantic 모델을 사용한 타입 안전성
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

#요청 스키마
class DetectScamRequest(BaseModel):
    """사기 탐지 요청"""

    model_config = ConfigDict(
        json_schema_extra={
            "examples":[
                {
                    "message": "금융감독원입니다. 안전계좌로 이체하세요.",
                    "sender": "02-1234-5678"
                }
            ]
        }
    )

    message: str = Field(
        ..., 
        description="분석할 메시지 (필수)", 
        min_length=1, 
        max_length=2000
    )
    sender: Optional[str] = Field(
        None, 
        description="발신자 정보 (선택)", 
        max_length=50
    )

#응답 스키마
class DetectScamResponse(BaseModel):
    """사기 탐지 응답"""

    model_config = ConfigDict(
        json_schema_extra={
            "examples":[
                {
                    "success": True,
                    "is_scam": True,
                    "scam_type": "보이스피싱",
                    "confidence": 0.9,
                    "risk_level": "매우높음",
                    "risk_score": 95,
                    "risk_factors": ["보이스피싱 패턴 감지", "높은 분류 신뢰도"],
                    "analysis": "매우 위험한 보이스피싱입니다...",
                    "recommendations": "즉시 신고하세요...",
                    "processing_time": 3.45,
                    "matched_patterns_count": 3,
                    "similar_cases_count": 5
                }
            ]
        }
    )

    #기본정보
    success: bool = Field(..., description="요청 성공 여부")
    
    # 분석 결과
    is_scam: bool = Field(..., description="사기 여부")
    scam_type: str = Field(..., description="사기 유형")
    confidence: float = Field(..., description="분류 신뢰도 (0-1)", ge=0.0, le=1.0)
    
    # 위험도
    risk_level: str = Field(..., description="위험도 레벨")
    risk_score: int = Field(..., description="위험도 점수 (0-100)", ge=0, le=100)
    risk_factors: List[str] = Field(default_factory=list, description="위험 요인 목록")
    
    # AI 분석
    analysis: str = Field(..., description="AI 종합 분석 내용")
    recommendations: str = Field(..., description="대응 방안 및 권장사항")
    
    # 메타데이터
    processing_time: float = Field(..., description="처리 시간 (초)", ge=0.0)
    matched_patterns_count: int = Field(..., description="매칭된 패턴 수", ge=0)
    similar_cases_count: int = Field(..., description="유사 사례 수", ge=0)

class ErrorResponse(BaseModel):
    """에러 응답"""
    
    success: bool = Field(default=False, description="요청 성공 여부")
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 내용")

class HealthCheckResponse(BaseModel):
    """헬스 체크 응답"""

    status: str = Field(..., description="서버 상태")
    version: str = Field(..., description="API 버전")
    timestamp: str = Field(..., description="현재 시각 (ISO 8601)")
    graph_loaded: bool = Field(..., description="그래프 로드 여부")
