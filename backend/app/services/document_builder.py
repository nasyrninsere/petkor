"""
API 응답 → 내부 PlaceDocument 변환 (정규화)
- 다양한 API 엔드포인트의 raw 응답을 일관된 형태로 정규화
"""
from typing import Dict, Optional
from app.models.schemas import PlaceDocument


def build_place_document(
    list_item: Dict,
    detail_common: Optional[Dict] = None,
    detail_pet: Optional[Dict] = None,
) -> PlaceDocument:
    """
    API 응답 데이터 → PlaceDocument 변환

    Args:
        list_item: petTourList API 응답 항목
        detail_common: detailCommon2 응답 (선택)
        detail_pet: detailPetTour2 응답 (선택)
    """
    # 기본 위치 정보
    content_id = str(list_item.get("contentid", ""))
    title = list_item.get("title", "이름 없음")
    addr = list_item.get("addr1", "") + " " + list_item.get("addr2", "")
    addr = addr.strip()

    # 좌표
    lat = _safe_float(list_item.get("mapy"))
    lng = _safe_float(list_item.get("mapx"))

    # 이미지 (firstimage 우선)
    image_url = (
        list_item.get("firstimage")
        or list_item.get("firstimage2")
        or None
    )

    # 상세 정보 (있을 때 우선)
    overview = None
    if detail_common:
        overview = detail_common.get("overview", "")
        if not image_url:
            image_url = detail_common.get("firstimage") or detail_common.get("firstimage2")
        if not lat:
            lat = _safe_float(detail_common.get("mapy"))
        if not lng:
            lng = _safe_float(detail_common.get("mapx"))

    # 반려동물 정보
    pet_info = None
    caution = None
    restrictions = None
    checkpoints = None

    if detail_pet:
        pet_info = detail_pet.get("acmpyPsblCpam", "")   # 동반 가능 동물
        caution = detail_pet.get("acmpyNeedMtr", "")     # 필요 준비물
        restrictions = detail_pet.get("relaAcmpyPsblCpam", "")  # 제한사항
        checkpoints = _build_checkpoints(detail_pet)

    # 반려동물 동반 가능 여부: 데이터가 있으면 True, 명시적 불가면 False
    pet_available = True
    if pet_info and ("불가" in pet_info or "금지" in pet_info):
        pet_available = False

    return PlaceDocument(
        contentId=content_id,
        contentTypeId=str(list_item.get("contenttypeid", "")),
        title=title,
        address=addr,
        lat=lat,
        lng=lng,
        imageUrl=image_url,
        overview=overview,
        petAvailable=pet_available,
        petInfo=pet_info,
        caution=caution,
        restrictions=restrictions,
        checkpoints=checkpoints,
    )


def _build_checkpoints(pet_detail: Dict) -> str:
    """반려동물 상세 정보에서 체크포인트 문자열 구성"""
    parts = []
    fields = {
        "acmpyPsblCpam": "동반 가능 동물",
        "acmpyNeedMtr": "필요 준비물",
        "relaAcmpyPsblCpam": "제한 사항",
        "etcAcmpyInfo": "기타 안내",
    }
    for key, label in fields.items():
        val = pet_detail.get(key, "").strip()
        if val:
            parts.append(f"• {label}: {val}")
    return "\n".join(parts) if parts else None


def _safe_float(val) -> Optional[float]:
    """안전한 float 변환"""
    try:
        return float(val) if val else None
    except (ValueError, TypeError):
        return None
