"""
사용자 자연어 질문 구조화 파서
- 규칙 기반으로 지역, 키워드, 반려동물 조건 등을 추출
- 확장 포인트: LLM 기반 파싱으로 교체 가능
"""
import re
from app.models.schemas import ParsedQuery


# ──────────────────────────────────────────────
# 사전 정의 매핑
# ──────────────────────────────────────────────
REGIONS = [
    "서울", "인천", "대전", "대구", "광주", "부산", "울산", "세종",
    "경기", "강원", "충북", "충남", "경북", "경남", "전북", "전남", "제주",
    "강릉", "속초", "춘천", "가평", "양평", "수원", "용인",
    "전주", "군산", "순천", "여수",
    "경주", "안동", "포항",
    "거제", "통영", "남해",
    "서귀포", "한라", "성산", "제주시",
]

PET_TYPES = {
    "강아지": "강아지", "개": "강아지", "반려견": "강아지", "독": "강아지",
    "고양이": "고양이", "반려묘": "고양이",
}

PET_SIZES = {
    "소형": "소형", "소형견": "소형", "작은": "소형",
    "중형": "중형", "중형견": "중형",
    "대형": "대형", "대형견": "대형", "큰": "대형",
}

PLACE_TYPE_KEYWORDS = {
    "실내": "indoor", "내부": "indoor", "카페": "indoor",
    "야외": "outdoor", "공원": "outdoor", "산책": "outdoor",
    "해변": "outdoor", "해수욕장": "outdoor", "산": "outdoor",
}

THEMES = {
    "산책": "산책", "워킹": "산책",
    "관람": "관람", "박물관": "관람", "전시": "관람",
    "사진": "사진", "포토": "사진",
    "캠핑": "캠핑", "글램핑": "캠핑",
    "수영": "수영", "해수욕": "수영",
    "카페": "카페", "맛집": "맛집", "식당": "맛집", "음식": "맛집",
    "가족": "가족여행", "아이": "가족여행",
    "숙박": "숙박", "펜션": "숙박", "호텔": "숙박",
}

INTENT_KEYWORDS = {
    "추천": "recommend", "좋은": "recommend", "알려줘": "recommend",
    "있어": "recommend", "있나요": "recommend", "어디": "recommend",
    "설명": "explain", "소개": "explain", "정보": "explain",
    "비교": "compare", "차이": "compare",
}


def parse_query(message: str) -> ParsedQuery:
    """
    사용자 메시지에서 구조화 정보 추출

    확장 포인트:
    - LLM 기반 파싱: OpenAI function calling / structured output 으로 교체 시
      이 함수의 시그니처와 반환 타입을 유지하고 내부 구현만 변경
    """
    msg = message.strip()

    # 1. 지역 추출
    region = None
    for r in sorted(REGIONS, key=len, reverse=True):  # 긴 이름 우선
        if r in msg:
            region = r
            break

    # 2. 반려동물 종류
    pet_type = None
    for keyword, pt in PET_TYPES.items():
        if keyword in msg:
            pet_type = pt
            break

    # 3. 반려동물 크기
    pet_size = None
    for keyword, ps in PET_SIZES.items():
        if keyword in msg:
            pet_size = ps
            break

    # 4. 실내/야외 구분
    place_type = None
    for keyword, pt in PLACE_TYPE_KEYWORDS.items():
        if keyword in msg:
            place_type = pt
            break

    # 5. 테마
    theme = None
    for keyword, t in THEMES.items():
        if keyword in msg:
            theme = t
            break

    # 6. 키워드 추출 (장소 유형 관련 단어)
    place_keywords = ["공원", "해변", "카페", "박물관", "전시", "산", "숲", "계곡",
                      "해수욕장", "펜션", "캠핑장", "글램핑", "호텔", "식당"]
    keyword = None
    for pk in place_keywords:
        if pk in msg:
            keyword = pk
            break

    # 7. 의도 분류
    intent = "recommend"
    for word, i in INTENT_KEYWORDS.items():
        if word in msg:
            intent = i
            break

    return ParsedQuery(
        intent=intent,
        region=region,
        keyword=keyword,
        pet_type=pet_type,
        pet_size=pet_size,
        place_type=place_type,
        theme=theme,
        raw_message=msg,
    )
