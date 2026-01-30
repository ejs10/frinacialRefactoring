"""
자동 크롤링 + 분석 스크립트

역할:
1. 웹 크롤링
2. 자동 분석
3. 결과 저장
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

PRPJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRPJECT_ROOT))

from agent.graph import get_graph
from agent.state import AgentState
from scripts.web_crawler import ScamNewsCrawler

async def analyze_news(graph, news_item: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
    """뉴스 분석"""
    print(f"\n[{index}] 분석 중: {news_item['title'][:50]}...")

    initial_state = {
        "message": news_item['title'] + "\n" + news_item.get('description', ''),
        "sender": None,
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
    try:
        result = await graph.ainvoke(initial_state)
        
        print(f"  → 사기 유형: {result.get('scam_type')}")
        print(f"  → 위험도: {result.get('risk_level')} ({result.get('risk_score')}점)")
        
        return {
            "news": news_item,
            "analysis": {
                "is_scam": result.get("is_scam"),
                "scam_type": result.get("scam_type"),
                "risk_level": result.get("risk_level"),
                "risk_score": result.get("risk_score"),
            }
        }
    except Exception as e:
        print(f"  ❌ 분석 실패: {e}")
        return None
    
async def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("🤖 자동 크롤링 + 분석 시스템")
    print("="*60)
    
    # Step 1: 크롤링
    print("\n[Step 1/3] 웹 크롤링 중...")
    crawler = ScamNewsCrawler()
    news_list = crawler.crawl_multiple_keywords(
        keywords=["보이스피싱", "대출사기"],
        max_per_keyword=5
    )
    print(f"✅ {len(news_list)}개 뉴스 수집")
    
    # Step 2: AI 에이전트 로드
    print("\n[Step 2/3] AI 에이전트 로드 중...")
    graph = get_graph()
    print("✅ 에이전트 준비 완료")
    
    # Step 3: 분석
    print("\n[Step 3/3] 뉴스 분석 중...")
    results: List[Dict[str, Any]] = []

    for idx, news in enumerate(news_list[:10], 1):
        result = await analyze_news(graph, news, idx)
        if result:
            results.append(result)
        await asyncio.sleep(1)
    
    output_dir = PRPJECT_ROOT / "data" / "analysis_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"auto_analysis_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 결과 저장: {output_file}")
    
    # 요약
    print("\n" + "="*60)
    print("📊 분석 요약")
    print("="*60)
    print(f"  크롤링: {len(news_list)}개")
    print(f"  분석 성공: {len(results)}개")
    
    scam_count = sum(1 for r in results if r['analysis'].get('is_scam'))
    print(f"  사기 판정: {scam_count}개")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())