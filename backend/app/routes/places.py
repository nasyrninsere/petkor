"""
/places 엔드포인트 라우터
- GET /places/search: 지역/키워드 기반 장소 검색
- GET /places/{contentId}: 장소 상세 조회
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from app.models.schemas import PlacesSearchResponse, PlaceDetail, PlaceDocument
from app.services.tourism_api import TourismAPIClient
from app.services.document_builder import build_place_document
from app.services.cache_service import get_cache_service, CacheService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/places", tags=["places"])

_api_client: TourismAPIClient = None


def get_api_client() -> TourismAPIClient:
    global _api_client
    if _api_client is None:
        _api_client = TourismAPIClient()
    return _api_client


@router.get("/search", response_model=PlacesSearchResponse)
async def search_places(
    region: Optional[str] = Query(None, description="지역명 (예: 강릉, 제주)"),
    keyword: Optional[str] = Query(None, description="검색 키워드"),
    lat: Optional[float] = Query(None, description="위도 (위치 기반 검색용)"),
    lng: Optional[float] = Query(None, description="경도 (위치 기반 검색용)"),
    radius: int = Query(5000, description="반경 (미터, 위치 기반 검색용)"),
    num_of_rows: int = Query(20, ge=1, le=50, description="결과 수"),
    cache: CacheService = Depends(get_cache_service),
):
    """
    장소 검색 API

    지도 이동, 필터 선택 시 사용.
    우선순위: 위치(lat/lng) > 지역명 > 키워드 전체 검색
    """
    client = get_api_client()

    # 캐시 키
    cache_key = cache.make_key("search", region, keyword, lat, lng, radius, num_of_rows)
    cached = await cache.get(cache_key)
    if cached:
        return PlacesSearchResponse(**cached)

    raw_items = []

    if lat and lng:
        # 위치 기반 검색
        raw_items = await client.search_by_location(
            map_x=lng, map_y=lat, radius=radius, num_of_rows=num_of_rows
        )
    elif region:
        area_code = client.get_area_code(region)
        raw_items = await client.search_by_area(
            area_code=area_code, keyword=keyword, num_of_rows=num_of_rows
        )
    elif keyword:
        raw_items = await client.search_by_keyword(keyword=keyword, num_of_rows=num_of_rows)
    else:
        # 기본: 전체 목록
        raw_items = await client.search_by_area(num_of_rows=num_of_rows)

    places = [build_place_document(item) for item in raw_items]

    result = PlacesSearchResponse(total=len(places), places=places)
    await cache.set(cache_key, result.model_dump(), ttl=3600)

    return result


@router.get("/{content_id}", response_model=PlaceDetail)
async def get_place_detail(
    content_id: str,
    cache: CacheService = Depends(get_cache_service),
):
    """
    장소 상세 조회

    detailCommon + detailPetTour + detailImage 를 합산해서 반환
    """
    client = get_api_client()

    # 캐시 확인
    cache_key = cache.make_key("detail", content_id)
    cached = await cache.get(cache_key)
    if cached:
        return PlaceDetail(**cached)

    import asyncio
    # 병렬로 상세 정보 조회
    detail_common, detail_pet, images_raw = await asyncio.gather(
        client.get_detail_common(content_id),
        client.get_detail_pet_tour(content_id),
        client.get_images(content_id),
        return_exceptions=True,
    )

    if isinstance(detail_common, Exception) or not detail_common:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다.")

    # 기본 문서 생성
    base_doc = build_place_document(
        list_item=detail_common,
        detail_common=detail_common,
        detail_pet=detail_pet if not isinstance(detail_pet, Exception) else None,
    )

    # 추가 이미지 목록
    extra_images = []
    if not isinstance(images_raw, Exception):
        extra_images = [
            img.get("originimgurl") or img.get("smallimageurl", "")
            for img in images_raw
            if img.get("originimgurl") or img.get("smallimageurl")
        ]

    detail = PlaceDetail(
        **base_doc.model_dump(),
        images=extra_images,
        tel=detail_common.get("tel"),
        homepage=detail_common.get("homepage"),
        useTime=detail_common.get("usetime"),
        parking=detail_common.get("parking"),
        restDate=detail_common.get("restdate"),
    )

    await cache.set(cache_key, detail.model_dump(), ttl=3600)
    return detail
