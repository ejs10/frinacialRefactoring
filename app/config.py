# Pydantic Settings 환경변수 관리
"""
애플리케이션 환경 설정

Pydantic Settings를 사용한 환경변수 관리
- .env 파일 자동 로드
- 타입 검증
- 기본값 설정
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 변수명: 타입 = Field()
    # 앱 기본 정보
    APP_NAME: str = Field(
        default="Scam Detection Agent", description="애플리케이션 이름"
    )
    APP_VERSION: str = Field(default="1.0.0", description="버전")
    DEBUG: bool = Field(default=False, description="디버그 모드")

    # API 설정
    API_HOST: str = Field(default="0.0.0.0", description="API 호스트")
    API_PORT: int = Field(default=8000, description="API 포트")

    #  Upstage API
    UPSTAGE_API_KEY: str = Field(..., description="Upstage API 키 (필수)")

    # LLM설정
    LLM_MODEL: str = Field(default="solar-pro", description="LLM 모델명")
    LLM_TEMPERATURE: float = Field(
        default=0.1, ge=0.0, le=2.0, description="LLM Temperature (0.0-2.0)"
    )

    LLM_MAX_TOKENS: int = Field(default=2000, ge=1, description="LLM 최대 토큰")

    # Embedding 설정
    EMBEDDING_MODEL: str = Field(
        default="solar-embedding-1-large", description="Embedding 모델명"
    )

    # ChromaDB 설정
    CHROMA_PATH: str = Field(
        default="data/chroma_scam_defense", description="ChromaDB 저장 경로"
    )

    CHROMA_COLLECTION: str = Field(
        default="scam_defense", description="ChromaDB 컬렉션명"
    )

    # 데이터경로
    SCAM_PATTERNS_FILE: str = Field(
        default="data/scam_defense/scam_patterns.json",
        description="사기 패턴 JSON 파일 경로",
    )

    # 타임아웃 설정
    REQUEST_TIMEOUT: int = Field(default=30, ge=1, description="API 요청 타임아웃 (초)")

    LLM_TIMEOUT: int = Field(default=25, ge=1, description="LLM API 타임아웃 (초)")

    # LangSmith
    LANGCHAIN_TRACING_V2: bool = Field(
        default=False, description="LangSmith 추적 활성화"
    )
    LANGCHAIN_API_KEY: Optional[str] = Field(
        default=None, description="LangSmith API 키"
    )
    LANGCHAIN_PROJECT: str = Field(
        default="scam-detection", description="LangSmith 프로젝트명"
    )

    # 설정 파일
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # Validator
    @field_validator("LLM_TEMPERATURE")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Temperature 범위 검증"""
        if not 0.0 <= v <= 2.0:
            raise ValueError("LLM_TEMPERATURE must be between 0.0 and 2.0")
        return v

    @field_validator("UPSTAGE_API_KEY")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """API 키 검증"""
        if not v or v.strip() == "":
            raise ValueError("UPSTAGE_API_KEY is required")
        return v.strip()


# 싱글톤 패턴
@lru_cache()
def get_settings() -> Settings:
    """
    설정 싱글톤

    앱 전체에서 동일한 설정 인스턴스 사용

    Returns:
        Settings 인스턴스
    """
    return Settings()


# 전역설정
settings = get_settings()


# 설정출력
def print_settings():
    """설정 정보 출력 (민감 정보 마스킹)"""
    s = get_settings()
    print("\n" + "=" * 60)
    print("📋 애플리케이션 설정")
    print("=" * 60)

    print(f"\n[앱 정보]")
    print(f"  이름: {s.APP_NAME}")
    print(f"  버전: {s.APP_VERSION}")
    print(f"  디버그: {s.DEBUG}")

    print(f"\n[API]")
    print(f"  호스트: {s.API_HOST}:{s.API_PORT}")

    print(f"\n[LLM]")
    print(f"  모델: {s.LLM_MODEL}")
    print(f"  Temperature: {s.LLM_TEMPERATURE}")
    print(f"  Max Tokens: {s.LLM_MAX_TOKENS}")
    print(f"  Timeout: {s.LLM_TIMEOUT}초")

    print(f"\n[ChromaDB]")
    print(f"  경로: {s.CHROMA_PATH}")
    print(f"  컬렉션: {s.CHROMA_COLLECTION}")

    print(f"\n[API 키]")
    # API 키 마스킹
    masked_key = s.UPSTAGE_API_KEY[:8] + "***" + s.UPSTAGE_API_KEY[-4:]
    print(f"  Upstage: {masked_key}")

    if s.LANGCHAIN_TRACING_V2:
        print(f"\n[LangSmith]")
        print(f"  활성화: {s.LANGCHAIN_TRACING_V2}")
        print(f"  프로젝트: {s.LANGCHAIN_PROJECT}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    # 테스트
    try:
        print_settings()
        print("✅ 설정 로드 성공!")
    except Exception as e:
        print(f"❌ 설정 로드 실패: {e}")
