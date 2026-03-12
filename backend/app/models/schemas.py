"""
API 요청/응답 및 내부 데이터 모델 정의
- Pydantic v2 기반 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional, List


# ──────────────────────────────────────────────
# 내부 데이터: 정규화된 장소 문서
# ──────────────────────────────────────────────
class PlaceDocument(BaseModel):
    """tourism_api + document_builder 에서 만들어내는 정규화 문서"""
    contentId: str
    contentTypeId: Optional[str] = None
    title: str
    address: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None
    imageUrl: Optional[str] = None
    overview: Optional[str] = None         # 기본 소개
    petAvailable: bool = True              # 반려동물 동반 가능 여부
    petInfo: Optional[str] = None          # 반려동물 관련 안내 원문
    caution: Optional[str] = None         # 주의사항
    restrictions: Optional[str] = None    # 제한사항 (크기, 종류 등)
    checkpoints: Optional[str] = None     # 방문 전 체크포인트
    score: float = 0.0                    # retriever 점수(내부용)


# ──────────────────────────────────────────────
# 질문 파싱 결과
# ──────────────────────────────────────────────
class ParsedQuery(BaseModel):
    """사용자 질문에서 추출된 구조화 정보"""
    intent: str = "recommend"             # recommend | explain | compare
    region: Optional[str] = None          # 강릉, 제주, 서울 등
    keyword: Optional[str] = None         # 산책, 카페, 해수욕장 등
    pet_type: Optional[str] = None        # 강아지, 고양이 등
    pet_size: Optional[str] = None        # 소형, 중형, 대형
    place_type: Optional[str] = None      # indoor | outdoor
    theme: Optional[str] = None           # 산책, 관람, 사진, 가족여행 등
    raw_message: str = ""


# ──────────────────────────────────────────────
# /chat 엔드포인트
# ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="사용자 질문")


class PlaceResult(BaseModel):
    """챗봇 응답에 포함되는 장소 카드"""
    contentId: str
    title: str
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    imageUrl: Optional[str] = None
    petAvailable: bool = True
    reason: Optional[str] = None          # 추천 이유 (LLM 생성)
    caution: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str                           # LLM 자연어 답변
    places: List[PlaceResult] = []
    parsed_query: Optional[ParsedQuery] = None


# ──────────────────────────────────────────────
# /places/search 엔드포인트
# ──────────────────────────────────────────────
class PlacesSearchResponse(BaseModel):
    total: int
    places: List[PlaceDocument]


# ──────────────────────────────────────────────
# /places/{contentId} 엔드포인트 (상세)
# ──────────────────────────────────────────────
class PlaceDetail(PlaceDocument):
    """상세 페이지용 - PlaceDocument 확장"""
    images: List[str] = []               # 추가 이미지 목록
    tel: Optional[str] = None
    homepage: Optional[str] = None
    useTime: Optional[str] = None
    parking: Optional[str] = None
    restDate: Optional[str] = None
