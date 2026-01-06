"""
대응 방안 생성 노드

역할:
- LLM을 사용하여 종합 분석 및 대응 방안 생성
- 사용자 친화적인 조언 제공
- 기존 scam_defense.py의 _generate_unified_answer() 로직 활용
"""

from typing import Dict, List, Optional
from agent.state import AgentState
from langchain_core.documents import Document


# 문서 포매팅 유틸리티
def format_documents(documents: List[Document], max_docs: int = 5) -> str:
    """
    문서 리스트를 텍스트로 포매팅

    Args:
        documents: 문서 리스트
        max_docs: 최대 문서 수

    Returns:
        포매팅된 텍스트
    """
    if not documents:
        return "관련정보 없음"

    formatted = []
    for idx, doc in enumerate(documents[:max_docs], 1):
        meta = doc.metadata or {}

        label = (
            meta.get("scam_type")
            or meta.get("source")
            or meta.get("title")
            or f"문서{idx}"
        )
        content = doc.page_content.strip()[:200]  # 최대200
        formatted.append(f"[{label}] {content}")

    return "\n\n".join(formatted)


def format_pattern_analysis(
    matched_patterns: List[Dict], risk_level: str, risk_score: int
) -> str:
    """
    패턴 분석 결과 포매팅

    Args:
        matched_patterns: 매칭된 패턴
        risk_level: 위험도 레벨
        risk_score: 위험도 점수

    Returns:
        포매팅된 텍스트
    """
    if not matched_patterns:
        return "매칭된 패턴 없음"

    lines = [f"위험도: {risk_level} ({risk_score}점)\n"]

    lines.append("매칭된 사기유형:")
    for pattern in matched_patterns[:5]:
        scam_type = pattern.get("scam_type", "알 수 없음")
        danger = pattern.get("danger_level", "정보")
        keywords = pattern.get("matched_patterns", [])

        kw_str = ", ".join(keywords[:3]) if keywords else "N/A"
        lines.append(f"- {scam_type} ({danger}): {kw_str}")
    return "\n".join(lines)


# LLM프롬포트
UNIFIED_SYSTEM_PROMPT = """
너는 금융사기 방지 전문 상담사다.
제공된 정보를 바탕으로 명확하고 실용적인 대응 가이드를 작성하라.

답변 구성:
1. 사기 여부 판단 및 위험도 평가
2. 사기 유형 및 수법 설명
3. 즉시 해야 할 대응 방법 (우선순위별 번호 목록)
4. 절대 하지 말아야 할 행동 (번호 목록)
5. 신고 방법 및 연락처
6. 예방 팁 및 주의사항

답변 형식:
- 위험도 아이콘 사용 (🚨 매우위험, ⚠️ 위험, ⚡ 주의, ℹ️ 안전)
- 명확하고 실행 가능한 조언
- 이해하기 쉬운 언어 사용
- 이모지 활용하여 가독성 향상

정확한 출처 문서를 근거로 답변하되, 의심스러운 경우 신중한 태도를 유지하라.
"""


def build_llm_prompt(
    message: str,
    sender: Optional[str],
    scam_type: str,
    risk_level: str,
    risk_score: int,
    matched_patterns: List[Dict],
    similar_cases: List[Document],
) -> str:
    """
    LLM 프롬프트 구성

    Args:
        message: 의심 메시지
        sender: 발신자
        scam_type: 사기 유형
        risk_level: 위험도 레벨
        risk_score: 위험도 점수
        matched_patterns: 매칭된 패턴
        similar_cases: 유사 사례

    Returns:
        프롬프트 텍스트
    """

    # RAG 문서
    rag_docs = [
        doc for doc in similar_cases if doc.metadata.get("origin") != "pattern_matching"
    ]

    # 패턴 문서 (실시간 매칭)
    pattern_docs = [
        doc for doc in similar_cases if doc.metadata.get("origin") == "pattern_matching"
    ]

    prompt = f"""
**의심 메시지:**
{message}

**발신자:** {sender or '미제공'}

**분석 결과:**
- 사기 유형: {scam_type}
- 위험도: {risk_level} ({risk_score}점)

**실시간 패턴 분석:**
{format_pattern_analysis(matched_patterns, risk_level, risk_score)}

**Knowledge Base (과거 유사 사례):**
{format_documents(rag_docs, max_docs=3)}

**실시간 사기 DB 매칭:**
{format_documents(pattern_docs, max_docs=3)}

위 정보를 바탕으로 즉시 대응 가이드를 작성하라.
"""

    return prompt

def generate_fallback_response(
    scam_type: str,
    risk_level: str,
    risk_score: int,
    is_scam: bool,
    risk_factors: List[str],
) -> str:
    """
    LLM 실패 시 fallback 응답 생성

    Args:
        scam_type: 사기 유형
        risk_level: 위험도 레벨
        risk_score: 위험도 점수
        is_scam: 사기 여부
        risk_factors: 위험 요인

    Returns:
        구조화된 fallback 응답
    """
    # 위험도에 따른 아이콘
    if risk_level == "매우높음":
        icon = "🚨"
        status = "매우 위험"
    elif risk_level == "높음":
        icon = "⚠️"
        status = "위험"
    elif risk_level == "중간":
        icon = "⚡"
        status = "주의 필요"
    else:
        icon = "ℹ️"
        status = "안전"
    response = f"""
{icon} **위험도 분석 결과**

**사기 여부:** {'🚨 사기로 판단됨' if is_scam else '✅ 정상으로 판단됨'}
**사기 유형:** {scam_type}
**위험도:** {risk_level} ({risk_score}점/100)
    """

    #위험 요인 표시
    if risk_factors:
        response += "**감지된 위험 요인:**\n"
        for idx, factor in enumerate(risk_factors, 1):
            response += f"{idx}. {factor}\n"

     # 사기로 판단된 경우
    if is_scam:
        response += """
**🛡️ 즉시 대응 방법**

1. ❌ **절대 돈을 보내지 마세요**
   - 어떤 명목으로든 입금/송금 금지
   - "안전계좌" 같은 것은 존재하지 않습니다

2. ❌ **개인정보를 제공하지 마세요**
   - 계좌번호, 비밀번호, 카드번호 등
   - 주민등록번호, OTP 인증번호 등

3. ❌ **링크를 클릭하지 마세요**
   - 의심스러운 URL은 피싱 사이트일 수 있습니다

4. 📞 **발신자 번호 차단**
   - 추가 연락 차단

5. 📱 **증거 수집 및 신고**
   - 메시지 스크린샷 저장
   - 아래 신고처에 즉시 신고

**📞 긴급 신고 연락처**

- **경찰청 사이버안전국:** 국번없이 **182**
- **금융감독원 불법금융신고센터:** **1332**
- **한국인터넷진흥원(KISA):** 국번없이 **118**
- **사이버캅 앱:** 스마트폰 앱 다운로드

**💡 예방 수칙**

✓ 공공기관은 전화로 금융정보를 요구하지 않습니다
✓ "안전계좌"는 존재하지 않습니다
✓ 의심되면 공식 홈페이지나 대표번호로 직접 확인하세요
✓ 급하게 결정하도록 압박하면 의심하세요

"""
    else:
        response += """
**✅ 정상 메시지로 판단**

현재 분석 결과 심각한 위험 징후는 발견되지 않았습니다.

**🛡️ 그래도 주의할 점**

- 의심스러운 점이 있다면 발신 기관에 직접 확인
- 개인정보나 금융정보 요구 시 신중하게 대응
- 링크 클릭 전 URL 확인

**📞 확인이 필요한 경우**

- 해당 기관 공식 홈페이지에서 대표번호 확인
- 직접 전화하여 사실 여부 확인

"""

    response += """
---
⚠️ **이 분석은 AI 기반 자동 분석입니다.**
최종 판단은 전문가와 상담하시기 바랍니다.
"""

    return response

# LLM호출
async def generate_with_llm(
    prompt: str, system_prompt: str = UNIFIED_SYSTEM_PROMPT,
    max_retries: int =2,
) -> str:
    """
    LLM으로 답변 생성

    Args:
        prompt: 사용자 프롬프트
        system_prompt: 시스템 프롬프트

    Returns:
        생성된 답변
    """
    try:
        from infrastructure.llm.client import UpstageClient
        from app.config import settings

        # LLM 클라이어트 생성
        llm = UpstageClient(
            api_key=settings.UPSTAGE_API_KEY,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
        )

        response = await llm.generate(prompt=prompt, system_prompt=system_prompt)

        return response.strip()

    except Exception as e:
        print(f"  ⚠️ LLM 호출 실패: {e}")

        # 폴백 응답
        return """
⚠️ AI 분석 생성 중 오류가 발생했습니다.

**긴급 상담:**
- 경찰청 사이버안전국: 국번없이 182
- 금융감독원: 1332
- 사이버캅 앱 다운로드

**기본 대응 방법:**
1. ❌ 절대 돈을 보내지 마세요
2. ❌ 개인정보를 제공하지 마세요
3. ❌ 링크를 클릭하지 마세요
4. 📞 발신자 차단
5. 📱 스크린샷 저장 후 신고

의심되는 메시지는 반드시 전문가와 상담하세요.
"""


# 메인 노드 함수
async def recommend_actions(state: AgentState) -> Dict:
    """
    대응 방안 생성 노드

    LLM을 사용하여:
    - 종합 분석
    - 대응 방안
    - 신고 방법

    Args:
        state: 에이전트 상태

    Returns:
        업데이트된 상태
    """
    print("\n" + "=" * 60)
    print("💡 [4/4] 대응 방안 생성 중...")
    print("=" * 60)

    # 상태에서 정보 추출
    message = state["message"]
    sender = state.get("sender")
    scam_type = state.get("scam_type")
    risk_level = state.get("risk_level", "알 수 없음")
    risk_score = state.get("risk_score", 0)
    is_scam = state.get("is_scam", False)
    risk_factors = state.get("risk_factors", [])
    matched_patterns = state.get("matched_patterns", [])
    similar_cases = state.get("similar_cases", [])

    print(f"  → 위험도: {risk_level} ({risk_score}점)")
    print(f"  → 사기 여부: {'예' if is_scam else '아니오'}")

    # LLM 프롬포트구성
    prompt = build_llm_prompt(
        message=message,
        sender=sender,
        scam_type=scam_type,
        risk_level=risk_level,
        risk_score=risk_score,
        matched_patterns=matched_patterns,
        similar_cases=similar_cases,
    )

    # LLM 호출
    print(f"  → LLM 호출 중...")

    analysis = await generate_with_llm(prompt)

    print(f"  → 분석 생성 완료 ({len(analysis)}자)")

    # 대응 방안은 analysis에 포함되어 있음
    recommendations = analysis

    # 상태 업데이트
    return {"analysis": analysis, "recommendations": recommendations, "completed": True}
