"""
LangGraph 상태 정의
에이전트가 워크플로우를 진행하며 공유하는 상태
"""

from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.documents import Document


class AgentState(TypedDict):
    """
    사기 탐지 에이전트 상태

    LangGraph의 각 노드가 이 상태를 읽고 수정함
    """

    # 입력
    message: str
    sender: Optional[str]

    # 분류 결과
    scam_type: Optional[str]
    confidence: Optional[float]

    # 검색 결과
    similar_cases: List[Document]
    matched_patterns: List[Dict]

    # 분석 결과
    risk_level: Optional[str]  # 위험도 레벨 (analyze 노드)
    risk_score: Optional[int]  # 위험도 점수 (0-100)
    risk_factors: List[str]  # 위험 요인

    # 최종 결과
    is_scam: Optional[bool]  # 사기 여부
    analysis: Optional[str]  # AI 분석 내용
    recommendations: Optional[str]  # 대응 방안 (recommend 노드)

    # 메타 정보
    processing_time: Optional[float]  # 처리 시간
    completed: bool  # 완료 여부
