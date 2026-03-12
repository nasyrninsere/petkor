"""
LLM 서비스: 프롬프트 구성 및 자연어 답변 생성
- OpenAI API 연동 (gpt-4o-mini 기본)
- OpenAI 없이도 규칙 기반 fallback 동작
- 확장 포인트: LangChain, Gemini, Claude 등으로 교체 가능
"""
import logging
from typing import List, Optional

from app.models.schemas import PlaceDocument, ParsedQuery, PlaceResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM 기반 응답 생성 서비스

    확장 포인트:
    - LangChain 연동: LLMChain → RAGChain으로 업그레이드
    - Streaming 응답: StreamingResponse 추가
    - Few-shot 예시: prompt에 examples 추가
    """

    def __init__(self):
        self.has_openai = bool(settings.OPENAI_API_KEY)
        if self.has_openai:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI 클라이언트 초기화 완료")
            except ImportError:
                logger.warning("openai 패키지 미설치 - fallback 모드로 동작")
                self.has_openai = False

    async def generate_answer(
        self,
        query: ParsedQuery,
        documents: List[PlaceDocument],
    ) -> tuple[str, List[PlaceResult]]:
        """
        장소 문서 기반 자연어 답변 생성

        Returns:
            (answer_text, place_results_with_reasons)
        """
        if not documents:
            return self._no_results_answer(query), []

        if self.has_openai:
            return await self._llm_answer(query, documents)
        else:
            return self._fallback_answer(query, documents)

    async def _llm_answer(
        self,
        query: ParsedQuery,
        documents: List[PlaceDocument],
    ) -> tuple[str, List[PlaceResult]]:
        """OpenAI API를 사용한 답변 생성"""
        doc_texts = self._format_documents(documents[:8])  # 비용 절감: 상위 8개만

        system_prompt = """당신은 반려동물 동반 여행 전문 AI 어시스턴트입니다.
제공된 장소 데이터만을 근거로 답변하세요.
데이터에 없는 내용은 절대 추측하지 마세요.
정보가 부족하면 "확인 필요"라고 표시하세요.

답변 형식:
- 2~3문장의 자연스러운 소개 문장
- 각 추천 장소마다: 장소명, 추천 이유, 반려동물 동반 가능 여부, 주의사항
- 마지막에 방문 전 팁 1~2줄"""

        user_prompt = f"""사용자 질문: {query.raw_message}

추출된 정보:
- 지역: {query.region or '미지정'}
- 반려동물: {query.pet_type or '반려동물'}
- 장소 유형: {query.place_type or '미지정'}
- 테마: {query.theme or '미지정'}

검색된 장소 정보:
{doc_texts}

위 장소들을 기반으로 자연스럽고 친근한 한국어로 답변해주세요."""

        try:
            resp = await self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=800,
            )
            answer = resp.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API 오류: {e}")
            _, places = self._fallback_answer(query, documents)
            return self._no_results_answer(query), places

        # PlaceResult 생성 (reason은 fallback으로 구성)
        places = self._build_place_results(documents)
        return answer, places

    def _fallback_answer(
        self,
        query: ParsedQuery,
        documents: List[PlaceDocument],
    ) -> tuple[str, List[PlaceResult]]:
        """OpenAI 없을 때 규칙 기반 답변 생성"""
        region_text = f"{query.region} 지역의 " if query.region else ""
        pet_text = f"{query.pet_type}와 " if query.pet_type else "반려동물과 "
        theme_text = f"{query.theme} " if query.theme else ""

        answer_lines = [
            f"🐾 {region_text}{pet_text}함께할 수 있는 {theme_text}여행지를 {len(documents)}곳 찾았습니다!\n"
        ]

        for i, doc in enumerate(documents[:5], 1):
            pet_ok = "✅ 반려동물 동반 가능" if doc.petAvailable else "⚠️ 동반 조건 확인 필요"
            caution = f"\n   - 주의: {doc.caution}" if doc.caution else ""
            answer_lines.append(
                f"**{i}. {doc.title}**\n"
                f"   📍 {doc.address}\n"
                f"   {pet_ok}{caution}"
            )

        answer_lines.append(
            "\n💡 방문 전 해당 장소에 직접 연락하여 반려동물 동반 조건을 다시 확인하시길 권장합니다."
        )

        places = self._build_place_results(documents)
        return "\n\n".join(answer_lines), places

    def _build_place_results(self, documents: List[PlaceDocument]) -> List[PlaceResult]:
        """PlaceDocument → PlaceResult 변환 (reason 자동 생성)"""
        results = []
        for doc in documents:
            reason = self._generate_reason(doc)
            results.append(PlaceResult(
                contentId=doc.contentId,
                title=doc.title,
                address=doc.address,
                lat=doc.lat,
                lng=doc.lng,
                imageUrl=doc.imageUrl,
                petAvailable=doc.petAvailable,
                reason=reason,
                caution=doc.caution,
            ))
        return results

    def _generate_reason(self, doc: PlaceDocument) -> str:
        """규칙 기반 추천 이유 생성"""
        if doc.overview:
            # 소개 첫 50자
            return doc.overview[:80].rstrip() + ("..." if len(doc.overview) > 80 else "")
        if doc.petInfo:
            return f"반려동물 동반 안내: {doc.petInfo[:60]}"
        return "반려동물과 함께 방문할 수 있는 여행지입니다."

    def _format_documents(self, documents: List[PlaceDocument]) -> str:
        """프롬프트용 문서 포맷"""
        lines = []
        for i, doc in enumerate(documents, 1):
            lines.append(f"""[{i}] {doc.title}
주소: {doc.address}
소개: {doc.overview or '정보 없음'}
반려동물 정보: {doc.petInfo or '정보 없음'}
주의사항: {doc.caution or '없음'}
제한사항: {doc.restrictions or '없음'}""")
        return "\n\n".join(lines)

    def _no_results_answer(self, query: ParsedQuery) -> str:
        region_text = f"{query.region} 지역에서 " if query.region else ""
        return (
            f"죄송합니다. {region_text}검색 조건에 맞는 반려동물 동반 여행지를 찾지 못했습니다. 🐾\n\n"
            "다른 지역이나 키워드로 다시 검색해 보시겠어요?\n"
            "예시: '서울에서 강아지랑 갈 수 있는 공원', '제주 반려견 동반 카페'"
        )
