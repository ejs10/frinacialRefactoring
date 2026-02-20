"""
개선된 ChromaDB 리포지토리

성능 개선 사항:
1. 배치 임베딩 (한 번에 여러 문서)
2. 임베딩 캐싱 (중복 방지)
3. 비동기 처리
"""

from pathlib import Path
from typing import Optional, List, Dict
import hashlib
import asyncio

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_upstage import UpstageEmbeddings
from functools import lru_cache


class ScamPatternRepository:
    """
    사기 패턴 검색 리포지토리 (기본 버전)
    """
    def __init__(
        self,
        collection_name: str = "scam_defense",
        persist_directory: Optional[str] = None,
    ) -> None:
        self.collection_name = collection_name

        if persist_directory:
            self.persist_directory = Path
            self.persist_directory = Path("data/chroma_scam_defense")

        self.persist_directory.mkdir(parents=True, exist_ok=True)

        from app.config import settings

        self.embeddings = UpstageEmbeddings(
            api_key=settings.UPSTAGE_API_KEY,
            model="solar-embedding-1-large",
        )

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory.absolute()),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        try:
            self.collection = self.client.get_or_create_collection(self.collection_name)
            print(f"[INFO] 컬렉션 로드: {self.collection_name} ({self.collection.count()}개 문서)")
        except Exception as e:
            print(f"[WARNING] 컬렉션 생성/로드: {e}")
            self.collection = self.client.create_collection(self.collection_name)

        self.vectorstore = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
        )
    def search(self, query: str, k: int = 5) -> List[Document]:
        """유사 문서 검색"""
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"  ⚠️ 검색 실패: {e}")
            return []
    def add_documents(self, documents: List[Document]) -> None:
        """문서 추가"""
        self.vectorstore.add_documents(documents)


class FastScamRepository:
    """
    고속 사기 패턴 검색 리포지토리
    
    성능 개선:
    - 배치 임베딩 (최대 100개씩)
    - LRU 캐싱
    - 비동기 처리
    """

    def __init__(
        self,
        collection_name: str = "scam_defense",
        persist_directory: Optional[str] = None,
        batch_size: int = 100) -> None:
        self.collection_name = collection_name
        self.batch_size = batch_size

        #ChromaDB경로
        if persist_directory:
            self.persist_directory = Path(persist_directory)
        else:
            self.persist_directory = Path("data/chroma_scam_defense")

        self.persist_directory.mkdir(parents=True, exist_ok=True)

        from app.config import settings

        self.embeddings = UpstageEmbeddings(
            api_key=settings.UPSTAGE_API_KEY,
            model="solar-embedding-1-large",
        )

        # ChromaDB 클라이언트
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory.absolute()),
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # 컬렉션 로드
        try:
            self.collection = self.client.get_or_create_collection(self.collection_name)
            print(f"[INFO] 컬렉션 로드: {self.collection_name} ({self.collection.count()}개 문서)")
        except Exception as e:
            print(f"[WARNING] 컬렉션 생성/로드: {e}")
            self.collection = self.client.create_collection(self.collection_name)

        self.vectorstore = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
        )

        self._embedding_cache: Dict[str, List[Document]] = {}

    @lru_cache(maxsize=1000)
    def _get_cache_key(self, text: str) -> str:
        """텍스트 해시 생성 (캐시 키)"""
        return hashlib.md5(text.encode()).hexdigest()
        
    def search(
        self,
        query: str,
        k: int = 5,
        use_cache: bool = True  
    ) -> List[Document]:
        """
        고속 검색
        
        Args:
            query: 검색 쿼리
            k: 결과 개수
            use_cache: 캐시 사용 여부
        
        Returns:
            유사 문서 리스트
        """
        #캐시확인
        if use_cache:
            cache_key = self._get_cache_key(query)
            if cache_key in self._embedding_cache:
                print(f"  ✓ 캐시에서 로드")
                return self._embedding_cache[cache_key][:k]

        try:    
            results = self.vectorstore.similarity_search(query, k=k)
            if use_cache:
                self._embedding_cache[cache_key] = results
            return results
        except Exception as e:
            print(f"  ⚠️ 검색 실패: {e}")
            return []
    
    async def search_async(
        self,
        query: str,
        k: int = 5
    ) -> List[Document]:
        """비동기 검색"""
        return await asyncio.to_thread(self.search, query, k)
    
    def add_documents_batch(
        self,
        documents: List[Document],
        batch_size: Optional[int] = None
    ) -> None:
        """
        배치로 문서 추가 (고속)
        
        Args:
            documents: 추가할 문서 리스트
            batch_size: 배치 크기 (기본값: self.batch_size)
        """
        if batch_size is None:
            batch_size = self.batch_size

        print(f"📝 {len(documents)}개 문서를 배치 추가 중...")

        #배치단위로 처리 
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]

            print(f"  [{i+1}-{min(i+batch_size, len(documents))}/{len(documents)}] 처리 중...")
            
            # 임베딩 + 저장
            self.vectorstore.add_documents(batch)

        print(f"✅ 배치 추가 완료!")   