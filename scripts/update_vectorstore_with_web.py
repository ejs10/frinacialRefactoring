"""
벡터 DB 업데이트 스크립트 (웹 크롤링 포함)

역할:
1. 웹에서 최신 사기 뉴스 크롤링
2. 고속 임베딩 (배치 처리)
3. ChromaDB에 추가
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.web_crawler import ScamNewsCrawler
from infrastructure.vector_store.scam_repository import FastScamRepository
from datetime import datetime

def update_vectorstore_with_web_data() -> bool:
    """
    웹 크롤링 데이터로 벡터 DB 업데이트
    """
    print("\n" + "="*60)
    print("🕷️ 웹 크롤링 + 벡터 DB 업데이트")
    print("="*60)
    
    # Step 1: 웹 크롤링
    print("\n[Step 1/3] 웹 크롤링 중...")
    crawler = ScamNewsCrawler()

    news_list = crawler.crawl_multiple_keywords(
        keywords=["보이스피싱", "메신저피싱", "스미싱", "대출사기", "투자사기"],
        max_per_keyword=10
    )
    print(f"✅ 총 {len(news_list)}개 뉴스 수집 완료")
    
    # Step 2: Document 변환
    print("\n[Step 2/3] Document 변환 중...")
    documents = crawler.convert_to_decuments(news_list)

    print(f"✅ {len(documents)}개 Document 생성 완료")
    
    # Step 3: 벡터 DB에 추가 (배치 처리)
    print("\n[Step 3/3] 벡터 DB 업데이트 중...")

    try:
        repo = FastScamRepository(batch_size=50)
        
        # 배치 추가 (고속)
        repo.add_documents_batch(documents, batch_size=50)
        
        print(f"✅ 벡터 DB 업데이트 완료!")
        print(f"   현재 총 문서 수: {repo.collection.count()}")
        
    except Exception as e:
        print(f"❌ 벡터 DB 업데이트 실패: {e}")
        return False
    
    # Step 4: 요약
    print("\n" + "="*60)
    print("📊 업데이트 요약")
    print("="*60)
    print(f"  크롤링 뉴스: {len(news_list)}개")
    print(f"  생성 Document: {len(documents)}개")
    print(f"  DB 총 문서: {repo.collection.count()}개")
    print(f"  업데이트 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = update_vectorstore_with_web_data()
    sys.exit(0 if success else 1)