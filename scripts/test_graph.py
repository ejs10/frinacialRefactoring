"""
LangGraph 워크플로우 테스트 스크립트

전체 사기 탐지 플로우를 테스트합니다.
"""

import asyncio
import time
from pathlib import Path
import sys
from typing import List, Tuple, Dict, Any

# 프로젝트 루트를 경로에 추가
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agent.graph import get_graph
from agent.state import AgentState


# ========== 테스트 케이스 ========== #

TEST_CASES = [
    {
        "name": "보이스피싱 (매우 위험)",
        "message": "안녕하세요. 금융감독원입니다. 귀하의 계좌가 범죄에 연루되어 금융거래가 정지되었습니다. 안전계좌로 즉시 이체하셔야 합니다.",
        "sender": "02-1234-5678",
    },
    {
        "name": "대출사기",
        "message": "무담보 대출 100% 승인! 저신용자도 가능합니다. 선입금 50만원만 입금하시면 즉시 대출 가능합니다.",
        "sender": "010-9876-5432",
    },
    {
        "name": "정상 메시지",
        "message": "KB국민은행입니다. 고객님의 계좌에서 50,000원이 출금되었습니다. 본인 거래가 아닌 경우 앱에서 확인하세요.",
        "sender": "1588-0000",
    },
]


# ========== 테스트 실행 함수 ========== #


async def test_single_case(graph, test_case: Dict[str, Any], case_num: int):
    """
    단일 테스트 케이스 실행

    Args:
        graph: LangGraph 워크플로우
        test_case: 테스트 케이스
        case_num: 케이스 번호
    """
    print("\n" + "=" * 80)
    print(f"테스트 케이스 #{case_num}: {test_case['name']}")
    print("=" * 80)

    print(f"\n📱 의심 메시지:")
    print(f"   {test_case['message']}")
    print(f"\n📞 발신자: {test_case['sender']}")

    # 초기 상태 생성
    initial_state = AgentState(
        message=test_case["message"],
        sender=test_case["sender"],
        scam_type=None,
        confidence=None,
        similar_cases=[],
        matched_patterns=[],
        risk_level=None,
        risk_score=None,
        risk_factors=[],
        is_scam=None,
        analysis=None,
        recommendations=None,
        processing_time=None,
        completed=False,
    )

    # 실행
    start_time = time.time()

    try:
        result = await graph.ainvoke(initial_state)
        elapsed = time.time() - start_time

        print("\n" + "=" * 80)
        print("✅ 분석 완료")
        print("=" * 80)

        print(f"\n⏱️  처리 시간: {elapsed:.2f}초")

        print(f"\n📊 분석 결과:")
        print(f"   사기 유형: {result.get('scam_type', 'N/A')}")
        print(f"   위험도: {result.get('risk_level', 'N/A')} ({result.get('risk_score', 0)}점)")
        print(f"   사기 여부: {'🚨 예 (사기)' if result.get('is_scam') else '✅ 아니오 (정상)'}")

        if result.get("risk_factors"):
            print(f"\n🔍 위험 요인:")
            for idx, factor in enumerate(result["risk_factors"], 1):
                print(f"   {idx}. {factor}")

        print(f"\n💡 AI 분석:")
        print("-" * 80)
        analysis = result.get("analysis", "분석 결과 없음")
        if len(analysis) > 500:
            print(analysis[:500] + "\n... (이하 생략)")
        else:
            print(analysis)
        print("-" * 80)

        return True

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ 에러 발생 ({elapsed:.2f}초)")
        print(f"   {type(e).__name__}: {e}")

        import traceback
        traceback.print_exc()

        return False


async def run_all_tests() -> None:
    """모든 테스트 케이스 실행"""
    print("\n" + "🎯" * 40)
    print("사기 탐지 LangGraph 워크플로우 테스트")
    print("🎯" * 40)

    print("\n[1/3] LangGraph 워크플로우 로드 중...")
    try:
        graph = get_graph()
        print("✅ 워크플로우 로드 완료")
    except Exception as e:
        print(f"❌ 워크플로우 로드 실패: {e}")
        return

    print(f"\n[2/3] 테스트 케이스 실행 ({len(TEST_CASES)}개)")

    results: List[Tuple[str, bool]] = []
    for idx, test_case in enumerate(TEST_CASES, 1):
        success = await test_single_case(graph, test_case, idx)
        results.append((test_case["name"], success))
        if idx < len(TEST_CASES):
            await asyncio.sleep(1)

    print("\n" + "=" * 80)
    print("[3/3] 테스트 결과 요약")
    print("=" * 80)

    success_count = sum(1 for _, success in results if success)
    total_count = len(results)

    for idx, (name, success) in enumerate(results, 1):
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{idx}. {name}: {status}")

    print("\n" + "=" * 80)
    print(f"총 {total_count}개 중 {success_count}개 성공 ({success_count / total_count * 100:.0f}%)")
    print("=" * 80)

    if success_count == total_count:
        print("\n🎉 모든 테스트 통과!")
    else:
        print(f"\n⚠️  {total_count - success_count}개 테스트 실패")


def main() -> int:
    """메인 함수"""
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⚠️  테스트 중단됨 (Ctrl+C)")
    except Exception as e:
        print(f"\n\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())