"""
/chat 엔드포인트 라우터
- POST /chat: 자연어 질문 → 장소 추천 + LLM 답변
"""
import json
import logging
from fastapi import APIRouter, HTTPException, Depends

from app.models.schemas import ChatRequest, ChatResponse
from app.services.tourism_api import TourismAPIClient
from app.services.query_parser import parse_query
from app.services.retriever import PlaceRetriever
from app.services.llm_service import LLMService
from app.services.cache_service import get_cache_service, CacheService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# 싱글톤 서비스 (앱 시작 시 초기화)
_api_client: TourismAPIClient = None
_llm_service: LLMService = None


def get_api_client() -> TourismAPIClient:
    global _api_client
    if _api_client is None:
        _api_client = TourismAPIClient()
    return _api_client


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    cache: CacheService = Depends(get_cache_service),
):
    """
    사용자 자연어 질문 처리

    Flow:
    1. 캐시 확인
    2. 질문 파싱 (지역, 키워드 등 추출)
    3. API로 후보 장소 검색 및 점수화
    4. LLM으로 자연어 답변 생성
    5. 결과 반환 + 캐시 저장
    """
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="빈 메시지입니다.")

    # 캐시 확인
    cache_key = cache.make_key("chat", message)
    cached = await cache.get(cache_key)
    if cached:
        logger.info(f"캐시 히트: {message[:30]}")
        return ChatResponse(**cached)

    # 질문 파싱
    parsed = parse_query(message)
    logger.info(f"파싱 결과: region={parsed.region}, keyword={parsed.keyword}, theme={parsed.theme}")

    # 후보 검색
    api_client = get_api_client()
    retriever = PlaceRetriever(api_client)
    documents = await retriever.retrieve(parsed, top_k=8)
    logger.info(f"검색된 장소 수: {len(documents)}")

    # LLM 답변 생성
    llm = get_llm_service()
    answer, places = await llm.generate_answer(parsed, documents)

    response = ChatResponse(
        answer=answer,
        places=places,
        parsed_query=parsed,
    )

    # 캐시 저장 (30분)
    await cache.set(cache_key, response.model_dump(), ttl=1800)

    return response
