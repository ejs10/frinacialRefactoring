"""
위험도 분석 노드

역할:
- 수집된 정보를 바탕으로 위험도 분석
- 위험도 점수 계산 (0-100)
- 위험 요인 추출
- 사기 여부 판단
"""

from typing import Dict, List
from agent.state import AgentState

# 위험도 계산
_DANGER_LEVEL_SCORE = {
    "매우높음": 30,
    "높음": 20,
    "중간": 10,
    "낮음": 5,
    "정보": 0,
}

_SCAM_TYPE_BASE_SCORE = {
    "보이스피싱": 40,
    "메신저피싱": 35,
    "스미싱": 30,
    "대출사기": 35,
    "투자사기": 30,
    "파밍": 35,
    "알 수 없음": 10,
}

# 점수쌓는부분
def calculate_risk_score(
        scam_type: str,
        confidence: float,
        matched_patterns: List[Dict],
        similar_cases: List
) -> tuple[int, List[str]]:
    """
    위험도 점수 및 요인 계산
    
    Args:
        scam_type: 사기 유형
        confidence: 분류 신뢰도
        matched_patterns: 매칭된 패턴
        similar_cases: 유사 사례
    
    Returns:
        (위험도 점수, 위험 요인 리스트)
    """
    risk_score = 0
    risk_factors = []

    #사기 유형 기본점수
    # 1. 사기 유형 기본 점수
    base_score = _SCAM_TYPE_BASE_SCORE.get(scam_type, 10)
    risk_score += base_score
    
    if scam_type != "알 수 없음":
        risk_factors.append(f"'{scam_type}' 패턴 감지")
    
    # 2. 분류 신뢰도 가중치
    confidence_score = int(confidence * 20)
    risk_score += confidence_score
    
    if confidence >= 0.8:
        risk_factors.append(f"높은 분류 신뢰도 ({confidence:.0%})")
    
    # 3. 매칭된 패턴 분석
    if matched_patterns:
        pattern_count = len(matched_patterns)
        pattern_score = pattern_count * 10
        risk_score += pattern_score
        
        # 위험도 레벨별 추가 점수
        for pattern in matched_patterns:
            danger = pattern.get("danger_level", "정보")
            danger_score = _DANGER_LEVEL_SCORE.get(danger, 0)
            risk_score += danger_score
            
            if danger in ["매우높음", "높음"]:
                scam_name = pattern.get("scam_type", "사기")
                risk_factors.append(f"'{scam_name}' 고위험 패턴 매칭")
        
        risk_factors.append(f"{pattern_count}개 사기 패턴 매칭")
    
    # 4. 유사 사례 개수
    if similar_cases:
        case_count = len(similar_cases)
        
        if case_count >= 5:
            risk_score += 15
            risk_factors.append(f"{case_count}개 유사 사기 사례 존재")
        elif case_count >= 3:
            risk_score += 10
            risk_factors.append(f"{case_count}개 유사 사기 사례 발견")
    
    # 최대값 제한
    risk_score = min(risk_score, 100)
    
    return risk_score, risk_factors


def get_risk_level(score: int) -> str:
    """
    위험도 점수를 레벨로 변환
    
    Args:
        score: 위험도 점수 (0-100)
    
    Returns:
        위험도 레벨
    """
    if score >= 80:
        return "매우높음"
    elif score >= 60:
        return "높음"
    elif score >= 40:
        return "중간"
    elif score >= 20:
        return "낮음"
    else:
        return "안전"


def determine_scam(risk_level: str, risk_score: int) -> bool:
    """
    사기 여부 판단
    
    Args:
        risk_level: 위험도 레벨
        risk_score: 위험도 점수
    
    Returns:
        사기 여부 (True/False)
    """
    # 위험도 60점 이상은 사기로 판단
    if risk_score >= 60:
        return True
    
    # 또는 위험도 레벨이 "높음" 이상
    if risk_level in ["매우높음", "높음"]:
        return True
    
    return False


# ========== 메인 노드 함수 ========== #

async def analyze_risk(state: AgentState) -> Dict:
    """
    위험도 분석 노드
    
    Args:
        state: 에이전트 상태
    
    Returns:
        업데이트된 상태
    """
    print("\n" + "="*60)
    print("⚠️  [3/4] 위험도 분석 중...")
    print("="*60)
    
    # 상태에서 정보 추출
    scam_type = state.get("scam_type", "알 수 없음")
    confidence = state.get("confidence", 0.5)
    matched_patterns = state.get("matched_patterns", [])
    similar_cases = state.get("similar_cases", [])
    
    print(f"  → 사기 유형: {scam_type} (신뢰도: {confidence:.0%})")
    print(f"  → 매칭 패턴: {len(matched_patterns)}개")
    print(f"  → 유사 사례: {len(similar_cases)}개")
    
    # 위험도 점수 계산
    risk_score, risk_factors = calculate_risk_score(
        scam_type=scam_type,
        confidence=confidence,
        matched_patterns=matched_patterns,
        similar_cases=similar_cases
    )
    
    # 위험도 레벨
    risk_level = get_risk_level(risk_score)
    
    # 사기 여부 판단
    is_scam = determine_scam(risk_level, risk_score)
    
    # 결과 출력
    print(f"\n  📊 분석 결과:")
    print(f"  → 위험도: {risk_level} ({risk_score}점)")
    print(f"  → 사기 여부: {'🚨 예 (사기)' if is_scam else '✅ 아니오 (정상)'}")
    
    if risk_factors:
        print(f"\n  🔍 위험 요인:")
        for idx, factor in enumerate(risk_factors, 1):
            print(f"    {idx}. {factor}")
    
    # 상태 업데이트
    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "is_scam": is_scam
    }