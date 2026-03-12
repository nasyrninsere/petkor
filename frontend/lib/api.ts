/**
 * 백엔드 API 클라이언트
 * - 환경변수 NEXT_PUBLIC_API_BASE_URL 기반
 * - 에러 처리 통일
 */
import type {
  ChatRequest,
  ChatResponse,
  PlaceDetail,
  PlacesSearchResponse,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchJSON<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new ApiError(
      res.status,
      (errorData as { detail?: string }).detail || `API 오류: ${res.status}`
    );
  }

  return res.json() as Promise<T>;
}

// ── 챗봇 ────────────────────────────────────
export async function sendChatMessage(
  message: string
): Promise<ChatResponse> {
  return fetchJSON<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ message } as ChatRequest),
  });
}

// ── 장소 검색 ────────────────────────────────
export async function searchPlaces(params: {
  region?: string;
  keyword?: string;
  lat?: number;
  lng?: number;
  radius?: number;
  num_of_rows?: number;
}): Promise<PlacesSearchResponse> {
  const qs = new URLSearchParams();
  if (params.region) qs.set("region", params.region);
  if (params.keyword) qs.set("keyword", params.keyword);
  if (params.lat) qs.set("lat", String(params.lat));
  if (params.lng) qs.set("lng", String(params.lng));
  if (params.radius) qs.set("radius", String(params.radius));
  if (params.num_of_rows) qs.set("num_of_rows", String(params.num_of_rows));

  return fetchJSON<PlacesSearchResponse>(
    `/places/search?${qs.toString()}`
  );
}

// ── 장소 상세 ────────────────────────────────
export async function getPlaceDetail(
  contentId: string
): Promise<PlaceDetail> {
  return fetchJSON<PlaceDetail>(`/places/${contentId}`);
}

export { ApiError };
