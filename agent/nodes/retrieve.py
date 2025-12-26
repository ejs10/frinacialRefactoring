"""
유사 사례 검색 및 패턴 매칭 노드 (RAG)

역할:
- ChromaDB에서 유사 사기 사례 검색 (벡터 검색)
- 실시간 패턴 분석 (scam_patterns.json)
- 병렬 처리로 속도 최적화

기존 scam_defense.py의 로직 활용
"""

import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import hashlib

from agent.state import AgentState
from langchain.schema import Document

_BASE_DIR = Path(__file__).resolve().parents[2]
_PATTERN_FILE = _BASE_DIR / "data" / "scam_defense" / "scam_patterns.json"
_PATTERN_CACHE: Optional[Dict] = None
_QUERY_CACHE: Dict[str, Tuple] = {}
_CACHE_SIZE_LIMIT = 100

_DANGER_LEVEL_ORDER = {
    "매우높음": 4,
    "높음": 3,
    "중간": 2,
    "낮음": 1,
    "정보": 0,
}


# ========== 유틸리티 함수 ========== #
@lru_cache(maxsize=1)
def _load_patterns() -> Dict:
    """패턴 JSON 로드(싱글톤)"""
    global _PATTERN_CACHE

    if _PATTERN_CACHE is not None:
        return _PATTERN_CACHE

    try:
        if _PATTERN_FILE.exists():
            with open(_PATTERN_FILE, "r", encoding="utf-8") as f:
                _PATTERN_CACHE = json.load(f)
                print(
                    f"  ✓ 패턴 로드: {len(_PATTERN_CACHE.get('financial_scams', []))}개"
                )
        else:
            print(f"  ⚠️ 패턴 파일 없음: {_PATTERN_FILE}")
            _PATTERN_CACHE = {}
    except Exception as e:
        print(f"  ⚠️ 패턴 로드 실패: {e}")
        _PATTERN_CACHE = {}
    return _PATTERN_CACHE


@lru_cache(maxsize=2048)
def _digits_only(value: Optional[str]) -> str:
    """숫자만 추출 (캐시)"""
    return "".join(ch for ch in (value or "") if ch.isdigit())


# 쿼리 해리 생성
def _hash_query(query: str, sender: Optional[str]) -> str:
    """쿼리 해시 생성 (캐시 키)."""
    key = f"{query}|{sender or ''}"
    return hashlib.md5(key.encode()).hexdigest()


def _clean_cache():
    """캐시 크기 제한."""
    global _QUERY_CACHE
    if len(_QUERY_CACHE) > _CACHE_SIZE_LIMIT:
        # 가장 오래된 절반 제거
        keys = list(_QUERY_CACHE.keys())
        for key in keys[: _CACHE_SIZE_LIMIT // 2]:
            _QUERY_CACHE.pop(key, None)


# ========== 실시간 패턴 분석 (기존로직 - 복붙) ========== #
def analyze_realtime_patterns(
    self, query: str, sender: Optional[str] = None
) -> Tuple[List[Document], Dict]:
    """실시간 패턴 분석 (기존 scam_defense.py 로직)

    Args:
        query: 분석할 메시지
        sender: 발신자 정보

    Returns:
        (패턴 문서 리스트, 분석 결과)"""
    # 캐시 확인
    cache_key = _hash_query(query, sender)
    if cache_key in _QUERY_CACHE:
        return _QUERY_CACHE[cache_key]

    # 패턴로드
    dataset = _load_patterns()
    if not dataset:
        result = ([], {})
        _QUERY_CACHE[cache_key] = result
        return result

    query_lower = query.strip().lower()
    if not query_lower:
        result = ([], {})
        _QUERY_CACHE[cache_key] = result
        return result

    sender_lower = (sender or "").strip().lower()
    query_digits = _digits_only(query)
    sender_digits = _digits_only(sender)

    pattern_docs = []
    scam_matches = []
    highest_score = -1
    highest_level = None

    # 1. 사기 패턴 매칭
    for scam in dataset.get("financial_scams", [])[:20]:  # 최대 20개만
        patterns = [
            p for p in scam.get("patterns", []) if p and p.lower() in query_lower
        ]
        # 발신자 패턴매칭
        sender_patterns = [
            p
            for p in scam.get("sender_patterns", [])
            if p
            and (
                p.lower() in query_lower or (sender_lower and p.lower() in sender_lower)
            )
        ]

        if not patterns and not sender_patterns:
            continue

        scam_type = scam.get("type", "알 수 없음")
        danger = scam.get("danger_level", "정보")
        score = _DANGER_LEVEL_ORDER.get(danger, -1)

        if score > highest_score:
            highest_score = score
            highest_level = danger

        # 간소화된 문서 생성
        content = f"유형: {scam_type} | 위험도: {danger}"
        if patterns:
            content += f"\n패턴: {', '.join(patterns[:3])}"  # 최대 3개

        pattern_docs.append(
            Document(
                page_content=content,
                metadata={
                    "source": "실시간패턴",
                    "scam_type": scam_type,
                    "danger_level": danger,
                    "origin": "pattern_matchinng",
                },
            )
        )

        scam_matches.append(
            {
                "scam_type": scam_type,
                "danger_level": danger,
                "matched_patterns": patterns[:3],  # 축소
            }
        )

    # 2. 키워드 매칭 (간소화)
    keyword_matches = {}
    for risk_level, keywords in (dataset.get("keywords") or {}).items():
        hits = [k for k in keywords[:10] if k and k.lower() in query_lower]  # 최대 10개
        if hits:
            keyword_matches[risk_level] = hits[:3]  # 축소
            score = _DANGER_LEVEL_ORDER.get(risk_level, -1)
            if score > highest_score:
                highest_score = score
                highest_level = risk_level

    # 3. 공식 연락처 (간소화)
    legitimate_matches = []
    for org, phone in list((dataset.get("legitimate_contacts") or {}).items())[
        :5
    ]:  # 최대 5개
        norm_phone = _digits_only(phone)
        if (org and org.lower() in query_lower) or (
            norm_phone and (norm_phone in query_digits or norm_phone in sender_digits)
        ):
            legitimate_matches.append({"organization": org, "phone": phone})
            pattern_docs.append(
                Document(
                    page_content=f"{org} 공식: {phone}",
                    metadata={"source": "공식연락처", "origin": "web_search"},
                )
            )

    # 결과 요약
    pattern_analysis = {
        "query": query.strip()[:100],  # 축소
        "sender": (sender or "").strip()[:50],
        "risk_summary": {
            "highest_level": highest_level,
            "score": highest_score,
            "is_high_risk": highest_score >= 3,
        },
        "scam_matches": scam_matches[:5],  # 최대 5개
        "keyword_matches": keyword_matches,
        "legitimate_contacts": legitimate_matches[:3],  # 최대 3개
    }

    result = (pattern_docs[:5], pattern_analysis)  # 최대 5개 문서

    # 캐시 저장
    _QUERY_CACHE[cache_key] = result
    _clean_cache()

    return result


# ========== RAG 검색 ========== #
def search_vector_store(query: str, k: int = 5) -> List[Document]:
    """
    ChromaDB에서 유사 사례 검색

    Args:
        query: 검색 쿼리
        k: 검색할 문서 수

    Returns:
        유사 문서 리스트
    """
    try:
        from infrastructure.vector_store.scam_repository import ChromaScamRepository
        from app.config import settings

        # 리포지토리 생성
        repo = ChromaScamRepository(
            persist_directory=settings.CHROMA_PATH,
            embedding_api_key=settings.UPSTAGE_API_KEY,
        )

        results = repo.search(query=query, k=k)
        return results
    except Exception as e:
        print(f"  ⚠️ ChromaDB 검색 실패: {e}")
        return []


async def retrieve_similar_cases(state: AgentState) -> Dict:
    """
    유사 사례 검색 노드 (RAG + 패턴 매칭)

    병렬 처리:
    - RAG 검색 (ChromaDB)
    - 실시간 패턴 분석 (JSON)

    Args:
        state: 에이전트 상태

    Returns:
        업데이트된 상태
    """
    print("\n" + "=" * 60)
    print("📚 [2/4] 유사 사례 검색 및 패턴 매칭 중...")
    print("=" * 60)

    message = state["message"]
    sender = state.get("sender")

    print(f"  → 검색 쿼리: {message[:50]}...")
    if sender:
        print(f"  → 발신자: {sender}")

    with ThreadPoolExecutor(max_workers=2) as executor:
        # rag검색
        rag_future = executor.submit(search_vector_store, message, 5)
        # 패턴검색
        pattern_future = executor.submit(analyze_realtime_patterns, message, sender)

        # 결과 수집 (타임아웃 1초)
        try:
            rag_docs = rag_future.result(timeout=1.0)
        except Exception:
            print(f"  ⚠️ RAG 검색 실패: {e}")
            rag_docs = []

        try:
            pattern_docs, pattern_analysis = pattern_future.result(timeout=2.0)
        except Exception:
            print(f"  ⚠️ 패턴 분석 실패: {e}")
            pattern_docs, pattern_analysis = [], {}
    print(f"  → RAG: {len(rag_docs)}개 유사 사례")
    print(f"  → 패턴: {len(pattern_docs)}개 매칭")

    # 패턴분석 결과출력
    if pattern_analysis:
        risk = pattern_analysis.get("risk_summary", {})
        if level := risk.get("highest_level"):
            print(f"  → 위험도: {level}")
        if matches := pattern_analysis.get("scam_matches"):
            print(f"  → {len(matches)}개 사기 유형 매칭")

    # 전체 문서 (RAG + 패턴)
    all_similar_cases = rag_docs + pattern_docs

    # 상태 업데이트
    return {
        "similar_cases": all_similar_cases,
        "matched_patterns": pattern_analysis.get("scam_matches", []),
    }
