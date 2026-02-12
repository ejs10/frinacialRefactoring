"""
벡터 DB 업데이트 스크립트 (웹 크롤링 포함)

역할:
1. 웹에서 최신 사기 뉴스 크롤링
2. 고속 임베딩 (배치 처리)
3. ChromaDB에 추가
"""

import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.web_crawler import ScamNewsCrawler
from infrastructure.vector_store.scam_repository import FastScamRepository
from datetime import datetime

DEFAULT_BATCH_SIZE = 50



def load_json_files(data_dir: str = "data") -> list:
    """
    data/ 폴더의 JSON 파일 로드

    list[dict] 형태면 그대로 사용
    """
    all_records = []
    data_path = Path(data_dir)
    if not data_path.exists():
        return all_records
    for json_file in data_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                # list[dict] 검증
                valid = [d for d in data if isinstance(d, dict) and d.get('title')]
                all_records.extend(valid)
                print(f"  📄 {json_file.name}: {len(valid)}개 로드")
            else:
                print(f"  ⚠️ {json_file.name}: list 형태가 아님, 스킵")
        except Exception as e:
            print(f"  ⚠️ {json_file.name} 로드 실패: {e}")
    return all_records

def load_csv_files(data_dir: str = "data") -> list:
    """
    data/ 폴더의 CSV 파일을 pandas로 읽어 records(dict list)로 변환
    """
    all_records = []
    data_path = Path(data_dir)
    if not data_path.exists():
        return all_records

    try:
        import pandas as pd
    except ImportError:
        print("  ⚠️ pandas 미설치, CSV 로드 스킵")
        return all_records

    for csv_file in data_path.glob("*.csv"):
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            records = df.to_dict('records')
            # 최소한 title 필드가 있는 레코드만
            valid = [r for r in records if r.get('title')]
            all_records.extend(valid)
            print(f"  📄 {csv_file.name}: {len(valid)}개 로드")
        except Exception as e:
            print(f"  ⚠️ {csv_file.name} 로드 실패: {e}")

    return all_records


def update_vectorstore_with_web_data(batch_size: int = DEFAULT_BATCH_SIZE) -> bool:
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

    # Step 2: data/ 폴더의 JSON, CSV 로드
    print("\n[Step 2/4] data/ 폴더 파일 로드 중...")
    json_records = load_json_files("data")
    csv_records = load_csv_files("data")

    print(f"  JSON: {len(json_records)}개 / CSV: {len(csv_records)}개")

    # 로컬 파일 레코드에 기본 필드 보완
    for record in json_records + csv_records:
        record.setdefault('source', 'local_file')
        record.setdefault('keyword', '')
        record.setdefault('crawled_at', datetime.now().isoformat())
        record.setdefault('description', '')
        record.setdefault('link', '')
        record.setdefault('press', '')
        record.setdefault('date', '')

    # Step 3: 합산 + 중복 제거
    print("\n[Step 3/4] 데이터 합산 + 중복 제거...")
    combined = news_list + json_records +csv_records
    combined = crawler.dedup_by_link(combined)
    print(f"  합산 후: {len(combined)}개")
    
    # Step 4: Document 변환
    documents = crawler.convert_to_documents(combined)

    print(f"✅ {len(documents)}개 Document 생성 완료")
    
    # Step 3: 벡터 DB에 추가 (배치 처리)
    print("\n[Step 3/3] 벡터 DB 업데이트 중...(배치: {batch_size})")

    try:
        repo = FastScamRepository(batch_size=batch_size)
        
        # 배치 추가 (고속)
        repo.add_documents_batch(documents, batch_size=batch_size)
        
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
    print(f"  JSON 파일: {len(json_records)}개")
    print(f"  CSV 파일: {len(csv_records)}개")
    print(f"  합산(dedup): {len(combined)}개")
    print(f"  생성 Document: {len(documents)}개")
    print(f"  DB 총 문서: {repo.collection.count()}개")
    print(f"  업데이트 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = update_vectorstore_with_web_data()
    sys.exit(0 if success else 1)