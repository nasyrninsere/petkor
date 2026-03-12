"""
후보 장소 검색 및 관련성 점수화
- ParsedQuery 기반으로 API를 호출하고 결과를 스코어링
- 확장 포인트: 벡터 DB 검색, 하이브리드 검색으로 교체 가능
"""
import asyncio
import logging
from typing import List

from app.models.schemas import ParsedQuery, PlaceDocument
from app.services.tourism_api import TourismAPIClient
from app.services.document_builder import build_place_document

logger = logging.getLogger(__name__)


class PlaceRetriever:
    """
    사용자 쿼리기반 장소 후보 검색 및 점수화

    확장 포인트:
    - 벡터 DB 연동: retrieve() 내부에서 벡터 검색 결과와 API 결과를 합산
    - LangChain retriever 인터페이스로 교체 가능
    """

    def __init__(self, client: TourismAPIClient):
        self.client = client

    async def retrieve(
        self,
        query: ParsedQuery,
        top_k: int = 10,
    ) -> List[PlaceDocument]:
        """
        질문 분석 결과로 API 호출 → 문서 변환 → 점수화 → 상위 반환

        전략:
        1. 지역 기반 검색 (region이 있을 때)
        2. 키워드 검색 (keyword가 있을 때)
        3. 결과 합산 후 중복 제거
        4. 점수화 후 정렬
        """
        area_code = None
        if query.region:
            area_code = self.client.get_area_code(query.region)

        raw_results = []

        # 검색 전략 실행 (병렬)
        tasks = []
        if query.region or area_code:
            tasks.append(self.client.search_by_area(
                area_code=area_code,
                keyword=query.keyword or query.theme,
                num_of_rows=30,
            ))
        if query.keyword:
            tasks.append(self.client.search_by_keyword(
                keyword=query.keyword,
                area_code=area_code,
                num_of_rows=20,
            ))
        if query.theme and query.theme != query.keyword:
            tasks.append(self.client.search_by_keyword(
                keyword=query.theme,
                area_code=area_code,
                num_of_rows=20,
            ))

        # 기본 전략: 파라미터가 없으면 한국 전체 반려동물 여행지 목록
        if not tasks:
            tasks.append(self.client.search_by_area(num_of_rows=30))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                raw_results.extend(result)

        # 중복 제거 (contentid 기준)
        seen = set()
        unique_items = []
        for item in raw_results:
            cid = item.get("contentid")
            if cid and cid not in seen:
                seen.add(cid)
                unique_items.append(item)

        # PlaceDocument 변환
        documents = [build_place_document(item) for item in unique_items]

        # 점수화
        scored = [self._score(doc, query) for doc in documents]
        scored.sort(key=lambda d: d.score, reverse=True)

        return scored[:top_k]

    def _score(self, doc: PlaceDocument, query: ParsedQuery) -> PlaceDocument:
        """
        관련성 점수 계산

        채점 기준:
        +2.0  지역명 주소 포함
        +1.5  제목에 키워드 포함
        +1.0  소개에 키워드 포함
        +1.0  반려동물 동반 정보 있음
        +0.5  실내/야외 조건 일치
        +0.5  이미지 있음 (정보 충실도)
        -1.0  좌표 없음 (지도 표시 불가)
        """
        score = 0.0
        title_lower = (doc.title or "").lower()
        addr_lower = (doc.address or "").lower()
        overview_lower = (doc.overview or "").lower()

        # 지역 매칭
        if query.region and query.region in (doc.address or ""):
            score += 2.0

        # 키워드 매칭
        for kw in [query.keyword, query.theme, query.pet_type]:
            if kw:
                if kw in title_lower:
                    score += 1.5
                elif kw in overview_lower:
                    score += 1.0

        # 실내/야외 조건
        if query.place_type == "indoor" and any(
            w in title_lower or w in overview_lower
            for w in ["실내", "카페", "갤러리", "박물관", "전시"]
        ):
            score += 0.5
        elif query.place_type == "outdoor" and any(
            w in title_lower or w in overview_lower
            for w in ["공원", "해변", "산", "숲", "야외", "광장"]
        ):
            score += 0.5

        # 반려동물 정보 충실도
        if doc.petInfo or doc.caution:
            score += 1.0

        # 이미지 있음
        if doc.imageUrl:
            score += 0.5

        # 좌표 없음 감점
        if not doc.lat or not doc.lng:
            score -= 1.0

        doc.score = round(score, 2)
        return doc
