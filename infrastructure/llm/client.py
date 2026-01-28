"""
Upstage LLM 클라이언트

역할:
- Upstage Solar LLM API 연동
- 비동기 호출 (asyncio)
- Timeout 관리
- 간단한 에러 처리
"""

import asyncio
from typing import Optional, List

from langchain_upstage import ChatUpstage
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage


class UpstageClient:
    """
    Upstage LLM 클라이언트

    Features:
    - 비동기 호출 (async/await)
    - Timeout 관리
    - 에러 처리

    Example:
        client = UpstageClient(
            api_key="your_api_key",
            model="solar-pro"
        )

        response = await client.generate(
            prompt="안녕하세요",
            system_prompt="당신은 친절한 AI입니다"
        )
    """

    def __init__(
        self,
        api_key: str,
        model: str = "solar-pro",
        temperature: float = 0.1,
        max_tokens: int = 2000,
        timeout: int = 25,
    ) -> None:
        """
        초기화

        Args:
            api_key: Upstage API 키
            model: 모델명 (solar-pro, solar-mini 등)
            temperature: 온도 (0.0-2.0)
            max_tokens: 최대 토큰 수
            timeout: 타임아웃 (초)
        """

        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

        # LangChain ChatUpstage 초기화
        self.llm = ChatUpstage(
            model=model,
            upstage_api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        print(f"✓ Upstage LLM 초기화: {model} (temp={temperature})")

    async def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        """
        텍스트 생성 (비동기)

        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트 (역할 정의)
            **kwargs: 추가 파라미터

        Returns:
            생성된 텍스트

        Raises:
            TimeoutError: 타임아웃 초과
            Exception: 기타 에러

        Example:
            response = await client.generate(
                prompt="금융사기란 무엇인가요?",
                system_prompt="당신은 금융 전문가입니다"
            )
        """
        # 메시지 구성
        messages: List[BaseMessage] = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        messages.append(HumanMessage(content=prompt))

        try:
            response = await asyncio.wait_for(
                self.llm.ainvoke(messages), timeout=self.timeout
            )

            return response.content

        except asyncio.TimeoutError:
            error_msg = f"LLM API 타임아웃: {self.timeout}초 초과"
            print(f"  ⚠️ {error_msg}")
            raise TimeoutError(error_msg)

        except Exception as e:
            error_msg = f"LLM API 에러: {str(e)}"
            print(f"  ⚠️ {error_msg}")
            raise Exception(error_msg)

    def generate_sync(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        """
        텍스트 생성 (동기)

        비동기 환경이 아닐 때 사용

        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            **kwargs: 추가 파라미터

        Returns:
            생성된 텍스트
        """
        messages: List[BaseMessage] = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        messages.append(HumanMessage(content=prompt))

        try:
            # 동기 호출
            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            error_msg = f"LLM API 에러: {str(e)}"
            print(f"  ⚠️ {error_msg}")
            raise Exception(error_msg)

    def __repr__(self) -> str:
        return (
            f"UpstageClient("
            f"model={self.model}, "
            f"temp={self.temperature}, "
            f"max_tokens={self.max_tokens}, "
            f"timeout={self.timeout}s"
            f")"
        )


def create_llm_client(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    timeout: Optional[int] = None,
) -> UpstageClient:
    """
    LLM 클라이언트 생성 (설정 자동 로드)

    Args:
        api_key: API 키 (None이면 설정에서 로드)
        model: 모델명 (None이면 설정에서 로드)
        temperature: 온도 (None이면 설정에서 로드)
        max_tokens: 최대 토큰 (None이면 설정에서 로드)
        timeout: 타임아웃 (None이면 설정에서 로드)

    Returns:
        UpstageClient 인스턴스

    Example:
        # 설정 파일에서 자동 로드
        client = create_llm_client()

        # 일부만 오버라이드
        client = create_llm_client(temperature=0.5)
    """
    from app.config import settings

    return UpstageClient(
        api_key=api_key or settings.UPSTAGE_API_KEY,
        model=model or settings.LLM_MODEL,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        max_tokens=max_tokens or settings.LLM_MAX_TOKENS,
        timeout=timeout or settings.LLM_TIMEOUT,
    )

def get_llm_client() -> ChatUpstage:
    """
    전역 LLM 클라이언트 싱글톤 반환

    Returns:
        ChatUpstage 인스턴스
    """
    from app.config import settings

    return ChatUpstage(
        model=settings.LLM_MODEL,
        upstage_api_key=settings.UPSTAGE_API_KEY,
        temperature=settings.LLM_TEMPERATURE,
    )


# 테스트 코드
async def _test_client() -> None:
    """클라이언트 테스트"""
    print("\n" + "=" * 60)
    print("Upstage LLM 클라이언트 테스트")
    print("=" * 60 + "\n")

    # 클라이언트 생성
    client = create_llm_client()
    print(f"클라이언트: {client}\n")

    # 테스트 프롬프트
    system_prompt = "당신은 금융사기 전문가입니다."
    user_prompt = "보이스피싱이란 무엇인가요? 간단히 설명해주세요."

    print(f"[시스템] {system_prompt}")
    print(f"[사용자] {user_prompt}\n")

    # 생성
    print("응답 생성 중...\n")

    try:
        response = await client.generate(
            prompt=user_prompt, system_prompt=system_prompt
        )

        print("=" * 60)
        print("응답:")
        print("=" * 60)
        print(response)
        print("=" * 60)
        print("\n✅ 테스트 성공!")

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")


if __name__ == "__main__":
    # 비동기 테스트 실행
    asyncio.run(_test_client())
