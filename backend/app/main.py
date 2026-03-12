"""
FastAPI 앱 진입점
- CORS 설정
- 라우터 등록
- 앱 시작/종료 이벤트
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import chat, places

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 이벤트"""
    logger.info(f"🐾 {settings.APP_TITLE} v{settings.APP_VERSION} 시작")
    logger.info(f"OpenAI 연동: {'활성화' if settings.OPENAI_API_KEY else '비활성화 (fallback 모드)'}")
    logger.info(f"Redis 캐시: {'활성화' if settings.REDIS_URL else '비활성화 (메모리 캐시)'}")
    yield
    logger.info("앱 종료")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="반려동물 동반여행 RAG 챗봇 API",
    lifespan=lifespan,
)

# ── CORS 설정 ──────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Vercel 배포 URL 와일드카드
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 라우터 등록 ────────────────────────────────
app.include_router(chat.router)
app.include_router(places.router)


# ── 헬스체크 ───────────────────────────────────
@app.get("/", tags=["health"])
async def root():
    return {
        "service": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "status": "ok",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}
