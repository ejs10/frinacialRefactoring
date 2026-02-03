"""
웹 크롤링 노드

역할:
- 네이버 뉴스에서 최신 사기 사례 크롤링
- 금감원, 경찰청 등 공식 정보 수집
- 크롤링 데이터를 Document로 변환
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
from langchain_core.documents import Document

class ScamNewsCrawler:
    """사기 뉴스 크롤러"""
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    def crawl_naver_news(
        self,
        keyword: str = "보이스피싱",
        max_count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        네이버 뉴스 크롤링
        
        Args:
            keyword: 검색 키워드
            max_count: 최대 수집 개수
        
        Returns:
            뉴스 리스트
        """
        print(f"\n🕷️ 네이버 뉴스 크롤링 중... (키워드: {keyword})")

        url = f"https://search.naver.com/search.naver?where=news&query={keyword}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text,'html.parser')

            news_list: List[Dict[str,Any]] = []
            # 뉴스 아이템 추출
            for idx, item in enumerate(soup.select('.news_area'), 1):
                if idx > max_count:
                    break
                
                try:
                    # 제목
                    title_elem = item.select_one('.news_tit')
                    title = title_elem.get_text().strip() if title_elem else ""
                    
                    # 요약
                    desc_elem = item.select_one('.news_dsc')
                    description = desc_elem.get_text().strip() if desc_elem else ""
                    
                    # 링크
                    link = title_elem.get('href') if title_elem else ""
                    
                    # 언론사
                    press_elem = item.select_one('.info.press')
                    press = press_elem.get_text().strip() if press_elem else ""
                    
                    # 날짜
                    date_elem = item.select_one('.info')
                    date = date_elem.get_text().strip() if date_elem else ""
                    
                    if title:
                        news_list.append({
                            'title': title,
                            'description': description,
                            'link': link,
                            'press': press,
                            'date': date,
                            'source': 'naver_news',
                            'keyword': keyword,
                            'crawled_at': datetime.now().isoformat()
                        })
                
                except Exception as e:
                    print(f"  ⚠️ 뉴스 파싱 실패: {e}")
                    continue
            
            print(f"  ✅ {len(news_list)}개 뉴스 수집 완료")
            return news_list
        
        except Exception as e:
            print(f"  ❌ 크롤링 실패: {e}")
            return []
        
    def crawl_multiple_keywords(
        self,
        keywords: Optional[List[str]] = None,
        max_per_keyword: int = 5
    ) -> List[Dict[str, Any]]:
        """
        여러 키워드로 크롤링
        
        Args:
            keywords: 키워드 리스트
            max_per_keyword: 키워드당 최대 개수
        
        Returns:
            전체 뉴스 리스트
        """
        if keywords is None:
            keywords = [
                "보이스피싱",
                "메신저피싱",
                "스미싱",
                "대출사기",
                "투자사기",
                "금융사기"
            ]
        all_news = []

        for keyword in keywords:
            news = self.crawl_naver_news(keyword, max_per_keyword)
            all_news.extend(news)
            time.sleep(1)

        return all_news
    def convert_to_documents(self, news_list: List[Dict[str,Any]]) -> List[Document]:
        """
        뉴스를 Document로 변환
        
        Args:
            news_list: 크롤링한 뉴스 리스트
        
        Returns:
            Document 리스트
        """
        documents = []

        for news in news_list:
            content = f"제목: {news['title']}\n"
            if news.get('description'):
                content += f"내용: {news['description']}\n"
            doc = Document(
                page_content=content,
                metadata={
                    'source': news['source'],
                    'keyword': news['keyword'],
                    'press': news.get('press', ''),
                    'date': news.get('date', ''),
                    'link': news.get('link', ''),
                    'crawled_at': news['crawled_at'],
                    'scam_type': news['keyword'],  # 키워드를 사기 유형으로 사용
                    'origin': 'web_crawling'
                }
            )
            documents.append(doc)
        return documents

# 사용 예시
if __name__ == "__main__":
    crawler = ScamNewsCrawler()
    
    # 크롤링
    news = crawler.crawl_multiple_keywords(max_per_keyword=3)
    
    # Document 변환
    documents = crawler.convert_to_documents(news)
    
    print(f"\n총 {len(documents)}개 Document 생성")
    
    # 첫 번째 문서 출력
    if documents:
        print(f"\n예시:")
        print(documents[0].page_content[:200])