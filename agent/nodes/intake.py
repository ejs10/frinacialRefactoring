"""
Intake 노드
입력 전처리 및 쿼리 리라이트
"""

from __future__ import annotations
import time
from typing import Any, Dict

from agent.state import ScamDefenseState, TraceInfo
from infrastructure.llm.client import get_llm_client

REWRITE_SYSTEM_PROMPT = """의심 메시지를 사기 패턴 검색 쿼리로 재작성하라.
핵심 키워드만 추출 (OTP, 계좌이체, 본인확인, 카드정지, 보이스피싱 등)
예: 'KB은행 OTP 알려주세요' → '금융기관 사칭 OTP 개인정보 요구'
쿼리만 반환."""

def intake_node(state: ScamDefenseState) -> Dict[str, Any]:
    """
    입력 전처리 노드
    
    책임:
    - 입력 검증
    - 쿼리 정규화
    - 검색용 쿼리 리라이트 (LLM)
    """
    start_time = time.time()
    errors: list = []

    query = (state.get("query") or "").strip()
    sender = (state.get("sender") or "").strip() or None

    #입력 검증
    if not query:
        return {
            "errors": ["쿼리가 비어있습니다."],
            "traces": state.get("traces", []) + [
                TraceInfo(
                    trace_id=state.get("trace_id", ""),
                    node_name="intake",
                    latency_ms=(time.time() - start_time) * 1000,
                    errors=["Empty query"],
                )
            ],
        }
    
    rewritten_query = query

    try:
        llm = get_llm_client()
        messages = [
            {"role":"system", "content": REWRITE_SYSTEM_PROMPT},
            {"role": "user", "content": query}
        ]
        response = llm.invoke(messages)
        rewritten = response.content.strip()
        if rewritten:
            rewritten_query = rewritten
    except Exception as e:
        errors.append(f"쿼리 리라이트 실패: {str(e)}")

    latency_ms = (time.time()-start_time) * 1000

    trace = TraceInfo(
        trace_id=state.get("trace_id", ""),
        node_name="intake",
        latency_ms=latency_ms,
        model_outputs_summary=f"rewritten: {rewritten_query[:50]}...",
        errors=errors if errors else [],
    )
    
    return {
        "query": query,
        "sender": sender,
        "rewritten_query": rewritten_query,
        "errors": state.get("errors", []) + errors,
        "traces": state.get("traces", []) + [trace],
    }