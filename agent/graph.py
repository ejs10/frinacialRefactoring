"""
LangGraph 워크플로우 정의
사기 탐지 에이전트의 핵심
"""

from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.classify import classify_scam_type
from agent.nodes.retrieve import retrieve_similar_cases
from agent.nodes.analyze import analyze_risk
from agent.nodes.generate import recommend_actions


def create_scam_detection_graph() -> StateGraph:
    """
    사기 탐지 그래프 생성

    워크플로우:
    START
      ↓
    classify (사기 유형 분류)
      ↓
    retrieve (유사 사례 검색 - RAG)
      ↓
    analyze (위험도 분석)
      ↓
    recommend (대응 방안 생성)
      ↓
    END

    Returns:
        컴파일된 StateGraph
    """

    # 그래프 생성
    workflow = StateGraph(AgentState)

    # 노드추가
    workflow.add_node("classify", classify_scam_type)
    workflow.add_node("retrieve", retrieve_similar_cases)
    workflow.add_node("analyze", analyze_risk)
    workflow.add_node("recommend", recommend_actions)

    # 엣지정의
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "retrieve")
    workflow.add_edge("retrieve", "analyze")
    workflow.add_edge("analyze", "recommend")
    workflow.add_edge("recommend", END)

    # 컴파일
    return workflow.compile()


# 전역 그래프를 인스턴스

# 앱 시작 시 한번만 생성하는 함수
_scam_detection_graph = None


def get_graph():
    """그래프 싱글톤"""
    global _scam_detection_graph
    if _scam_detection_graph is None:
        print("🔨 LangGraph 워크플로우 생성 중...")
        _scam_detection_graph = create_scam_detection_graph()
        print("✅ LangGraph 워크플로우 준비 완료!")
    return _scam_detection_graph


if __name__ == "__main__":
    # 그래프 시각화 (선택)
    graph = create_scam_detection_graph()

    # 테스트 실행
    result = graph.invoke(
        {
            "message": "금융감독원입니다. 안전계좌로 긴급 이체하세요.",
            "sender": "010-1234-5678",
            "completed": False,
        }
    )

    print("\n" + "=" * 60)
    print("테스트 결과:")
    print("=" * 60)
    print(f"사기 여부: {result.get('is_scam')}")
    print(f"위험도: {result.get('risk_level')} ({result.get('risk_score')}점)")
    print(f"분석: {result.get('analysis', '')[:100]}...")
    print("=" * 60)
