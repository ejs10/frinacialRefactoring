"""
FastAPI 의존성 주입

LangGraph 워크플로우를 싱글톤으로 관리
"""

from functools import lru_cache
from agent.graph import get_graph

class GraphMamager:
    """
    LangGraph 워크플로우 매니저 (싱글톤)
    
    앱 시작 시 한 번만 그래프를 로드하고 재사용
    """

    _instance = None
    _graph = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self):
        """그래프 초기화"""
        if self._graph is None:
            print()
            self._graph = get_graph()
            print()
        return self._graph
    
    def get_graph(self):
        """그래프 반환"""
        if self._graph is None:
            return self.initialize
        return self._graph
    
#전역 진스턴스
graph_manager = GraphMamager()

@lru_cache()
def get_graph_instance():
    """
    의존성 주입용 함수
    
    FastAPI 엔드포인트에서 사용
    """
    return graph_manager.get_graph()