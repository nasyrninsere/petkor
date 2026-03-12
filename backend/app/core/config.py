"""
환경변수 및 앱 설정 관리
- pydantic-settings를 사용한 타입 안전한 설정 관리
- .env 파일에서 자동으로 환경변수 로드
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # === 한국관광공사 API ===
    TOUR_API_KEY: str = "d5c9cc9debf7cdab53435da4518723b5e860ff13c9987dd798505afdc94d432d"
    TOUR_API_BASE_URL: str = "https://apis.data.go.kr/B551011/KorPetTourService2"

    # === OpenAI (LLM) ===
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # === Redis 캐시 (선택사항) ===
    REDIS_URL: str = ""
    CACHE_TTL: int = 3600  # 1시간

    # === 앱 설정 ===
    APP_TITLE: str = "🐾 펫 트래블 RAG 챗봇"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    # 배포 시 Railway 환경변수에서 Vercel URL을 포함한 값으로 덮어쓰세요:
    # CORS_ORIGINS=["https://your-app.vercel.app","http://localhost:3000"]
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 반환 (캐시됨)"""
    return Settings()


settings = get_settings()
