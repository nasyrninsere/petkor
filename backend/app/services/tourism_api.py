"""
한국관광공사 반려동물 동반여행 Open API 래퍼
Base URL: https://apis.data.go.kr/B551011/KorPetTourService2
- 모든 외부 API 호출을 이 모듈에서 담당
"""
import httpx
import logging
from typing import Optional, List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class TourismAPIClient:
    """한국관광공사 KorPetTourService2 API 클라이언트"""

    BASE_URL = settings.TOUR_API_BASE_URL  # https://apis.data.go.kr/B551011/KorPetTourService2
    API_KEY = settings.TOUR_API_KEY

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=15.0)

    def _base_params(self, **extra) -> Dict[str, Any]:
        """공통 파라미터 구성"""
        params: Dict[str, Any] = {
            "serviceKey": self.API_KEY,
            "MobileOS": "ETC",
            "MobileApp": "PetTravelApp",
            "_type": "json",
            "numOfRows": extra.pop("numOfRows", 20),
            "pageNo": extra.pop("pageNo", 1),
        }
        params.update(extra)
        return params

    async def _get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """공통 GET 요청 + 응답 파싱"""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            resp = await self._client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", {})
        except httpx.HTTPStatusError as e:
            logger.error(f"API HTTP 오류 [{e.response.status_code}]: {url}")
            return {}
        except Exception as e:
            logger.error(f"API 요청 실패 [{url}]: {e}")
            return {}

    def _extract_items(self, response: Dict) -> List[Dict]:
        """응답 body.items.item 추출 (단일 객체/배열/빈값 처리)"""
        try:
            items = response.get("body", {}).get("items", {})
            if not items or items == "":
                return []
            item = items.get("item", [])
            if isinstance(item, dict):
                return [item]
            return item or []
        except Exception:
            return []

    # ──────────────────────────────────────────────────
    # 1. 지역 기반 반려동물 여행 목록 조회 (areaBasedList2)
    # ──────────────────────────────────────────────────
    async def search_by_area(
        self,
        area_code: Optional[str] = None,
        sigungu_code: Optional[str] = None,
        keyword: Optional[str] = None,
        num_of_rows: int = 20,
    ) -> List[Dict]:
        """지역코드 기반 반려동물 동반 장소 목록"""
        params = self._base_params(numOfRows=num_of_rows, arrange="O")
        if area_code:
            params["areaCode"] = area_code
        if sigungu_code:
            params["sigunguCode"] = sigungu_code

        resp = await self._get("areaBasedList2", params)
        items = self._extract_items(resp)

        # 키워드 필터 (클라이언트 사이드)
        if keyword and items:
            kw = keyword.lower()
            filtered = [
                it for it in items
                if kw in (it.get("title") or "").lower()
                or kw in (it.get("addr1") or "").lower()
            ]
            return filtered if filtered else items  # 필터 결과 없으면 전체 반환

        return items

    # ──────────────────────────────────────────────────
    # 2. 키워드 검색 (searchKeyword2)
    # ──────────────────────────────────────────────────
    async def search_by_keyword(
        self,
        keyword: str,
        area_code: Optional[str] = None,
        num_of_rows: int = 20,
    ) -> List[Dict]:
        """키워드로 반려동물 여행지 검색"""
        params = self._base_params(numOfRows=num_of_rows, keyword=keyword)
        if area_code:
            params["areaCode"] = area_code

        resp = await self._get("searchKeyword2", params)
        return self._extract_items(resp)

    # ──────────────────────────────────────────────────
    # 3. 위치 기반 주변 검색 (locationBasedList2)
    # ──────────────────────────────────────────────────
    async def search_by_location(
        self,
        map_x: float,
        map_y: float,
        radius: int = 5000,
        num_of_rows: int = 20,
    ) -> List[Dict]:
        """위도/경도 중심 반경 내 장소 검색 (radius 단위: m)"""
        params = self._base_params(
            numOfRows=num_of_rows,
            mapX=map_x,
            mapY=map_y,
            radius=radius,
        )
        resp = await self._get("locationBasedList2", params)
        return self._extract_items(resp)

    # ──────────────────────────────────────────────────
    # 4. 공통 상세 조회 (detailCommon2)
    # ──────────────────────────────────────────────────
    async def get_detail_common(self, content_id: str) -> Dict:
        """contentId로 기본 상세 정보 조회"""
        params = self._base_params(
            contentId=content_id,
            defaultYN="Y",
            firstImageYN="Y",
            areacodeYN="Y",
            catcodeYN="Y",
            addrinfoYN="Y",
            mapinfoYN="Y",
            overviewYN="Y",
        )
        resp = await self._get("detailCommon2", params)
        items = self._extract_items(resp)
        return items[0] if items else {}

    # ──────────────────────────────────────────────────
    # 5. 반려동물 동반여행 상세 조회 (detailPetTour2)
    # ──────────────────────────────────────────────────
    async def get_detail_pet_tour(self, content_id: str) -> Dict:
        """반려동물 특화 상세 정보 (동반 가능 여부, 제한사항 등)"""
        params = self._base_params(contentId=content_id)
        resp = await self._get("detailPetTour2", params)
        items = self._extract_items(resp)
        return items[0] if items else {}

    # ──────────────────────────────────────────────────
    # 6. 이미지 목록 조회 (detailImage2)
    # ──────────────────────────────────────────────────
    async def get_images(self, content_id: str) -> List[Dict]:
        """콘텐츠의 추가 이미지 목록"""
        params = self._base_params(
            contentId=content_id,
            imageYN="Y",
            subImageYN="Y",
        )
        resp = await self._get("detailImage2", params)
        return self._extract_items(resp)

    # ──────────────────────────────────────────────────
    # 지역명 → 지역코드 매핑 (한국관광공사 areaCode 기준)
    # ──────────────────────────────────────────────────
    AREA_CODES: Dict[str, str] = {
        "서울": "1", "인천": "2", "대전": "3", "대구": "4",
        "광주": "5", "부산": "6", "울산": "7", "세종": "8",
        "경기": "31", "강원": "32", "충북": "33", "충남": "34",
        "경북": "35", "경남": "36", "전북": "37", "전남": "38",
        "제주": "39",
        # 주요 시·군·구 별칭 → 광역 코드 매핑
        "강릉": "32", "속초": "32", "춘천": "32", "원주": "32",
        "전주": "37", "군산": "37",
        "여수": "38", "순천": "38",
        "경주": "35", "안동": "35", "포항": "35",
        "거제": "36", "통영": "36", "남해": "36",
        "제주시": "39", "서귀포": "39",
        "수원": "31", "용인": "31", "가평": "31", "양평": "31",
    }

    def get_area_code(self, region_name: str) -> Optional[str]:
        """지역명 → 지역코드 변환 (부분 매칭)"""
        for key, code in self.AREA_CODES.items():
            if key in region_name:
                return code
        return None

    async def close(self):
        await self._client.aclose()
