"""
사기 유형 분류 노드

역할:
- 패턴 분석 결과를 바탕으로 사기 유형 분류
- 간단하고 빠르게 (복잡한 LLM 호출 없이)
"""

from typing import Dict
from agent.state import AgentState


async def classify_scam_type(state: AgentState) -> Dict:
    """
    사기 유형 분류 (간단 버전)

    Args:
        state: 에이전트 상태

    Returns:
        업데이트된 상태 (scam_type, confidence 추가)
    """
    print("\n" + "=" * 60)
    print("🔍 [1/4] 사기 유형 분류 중...")
    print("=" * 60)

    message = state["message"]
    message_lower = message.lower()

    # 간닪한 키워드 기반 분류
    scam_type = "알 수 없음"
    confidence = 0.5

    # 보이스피싱
    if any(
        kw in message_lower
        for kw in [
            "검찰",
            "경찰",
            "금융감독원",
            "금감원",
            "안전계좌",
            "계좌이체",
            "금융거래정지",
            "검사",
            "형사",
            "경위",
        ]
    ):
        scam_type = "보이스피싱"
        confidence = 0.9

    # 메신저피싱
    elif any(
        kw in message_lower
        for kw in [
            "엄마",
            "아빠",
            "아들",
            "딸",
            "카톡",
            "카카오톡",
            "텔레그램",
            "급해",
            "긴급",
            "계좌번호",
        ]
    ):
        scam_type = "메신저피싱"
        confidence = 0.85

    # 스미싱
    elif any(
        kw in message_lower
        for kw in ["http", "https", "bit.ly", "링크", "클릭", "확인", "택배", "배송"]
    ):
        scam_type = "스미싱"
        confidence = 0.8

    # 대출사기
    elif any(
        kw in message_lower
        for kw in [
            "대출",
            "무담보",
            "신용회복",
            "선입금",
            "100% 승인",
            "즉시대출",
            "저신용",
        ]
    ):
        scam_type = "대출사기"
        confidence = 0.85

    # 투자사기
    elif any(
        kw in message_lower
        for kw in ["투자", "수익률", "코인", "가상화폐", "주식", "선물", "환전"]
    ):
        scam_type = "투자사기"
        confidence = 0.8

    print(f"  → 분류: {scam_type}")
    print(f"  → 신뢰도: {confidence:.2f}")

    # 상태 업데이트
    return {"scam_type": scam_type, "confidence": confidence}
