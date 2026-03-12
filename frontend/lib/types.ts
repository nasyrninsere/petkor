// === 공유 타입 정의 ===
// 백엔드 API 스키마와 동기화

/** 챗봇 채팅 메시지 */
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  places?: PlaceResult[];
  timestamp: Date;
}

/** 챗봇 응답에 포함되는 장소 카드 */
export interface PlaceResult {
  contentId: string;
  title: string;
  address: string;
  lat?: number;
  lng?: number;
  imageUrl?: string;
  petAvailable: boolean;
  reason?: string;
  caution?: string;
}

/** 장소 상세 정보 */
export interface PlaceDetail extends PlaceResult {
  overview?: string;
  petInfo?: string;
  restrictions?: string;
  checkpoints?: string;
  images: string[];
  tel?: string;
  homepage?: string;
  useTime?: string;
  parking?: string;
  restDate?: string;
}

/** /chat API 요청 */
export interface ChatRequest {
  message: string;
}

/** /chat API 응답 */
export interface ChatResponse {
  answer: string;
  places: PlaceResult[];
  parsed_query?: ParsedQuery;
}

/** 파싱된 쿼리 */
export interface ParsedQuery {
  intent: string;
  region?: string;
  keyword?: string;
  pet_type?: string;
  pet_size?: string;
  place_type?: string;
  theme?: string;
  raw_message: string;
}

/** /places/search 응답 */
export interface PlacesSearchResponse {
  total: number;
  places: PlaceResult[];
}

/** 필터 상태 */
export interface FilterState {
  region: string;
  keyword: string;
  placeType: "all" | "indoor" | "outdoor";
}

/** 지도 마커 */
export interface MapMarker {
  contentId: string;
  title: string;
  lat: number;
  lng: number;
  petAvailable: boolean;
}
