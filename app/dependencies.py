"""
FastAPI 의존성 주입

LangGraph 워크플로우를 싱글톤으로 관리
"""

from functools import lru_cache
from agent.graph import get_graph

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph

class GraphMamager:
    """
    LangGraph 워크플로우 매니저 (싱글톤)
    
    앱 시작 시 한 번만 그래프를 로드하고 재사용
    """

    _instance: Optional["GraphMamager"] = None
    _graph: Optional["CompiledStateGraph"] = None

    def __new__(cls) -> "GraphMamager" :
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self) -> "CompiledStateGraph":
        """그래프 초기화"""
        if self._graph is None:
            from agent.graph import get_graph
            print("\n🔨 LangGraph 워크플로우 초기화 중...")
            self._graph = get_graph()
            print("LangGraph 워크플로우 준비 완료!\n")
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
    """
    return graph_manager.get_graph()