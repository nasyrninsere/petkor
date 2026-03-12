"use client";

/**
 * 메인 페이지
 * - 레이아웃: 상단 헤더 / 중단(지도+챗봇) / 하단 카드 리스트
 * - 상태 통합 관리: 추천 장소, 선택된 장소, 상세 모달
 */
import { useState, useCallback } from "react";
import dynamic from "next/dynamic";
import type { PlaceResult, PlaceDetail, FilterState } from "@/lib/types";
import { getPlaceDetail, searchPlaces } from "@/lib/api";
import ChatPanel from "@/components/ChatPanel";
import PlaceList from "@/components/PlaceList";
import FilterBar from "@/components/FilterBar";
import PlaceDetailModal from "@/components/PlaceDetailModal";
import styles from "./page.module.css";

// MapView는 카카오맵 SDK 의존성으로 CSR(클라이언트 사이드)에서만 렌더링
const MapView = dynamic(() => import("@/components/MapView"), { ssr: false });

export default function HomePage() {
  const [places, setPlaces] = useState<PlaceResult[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isFilterLoading, setIsFilterLoading] = useState(false);

  // 상세 모달
  const [modalPlace, setModalPlace] = useState<PlaceDetail | null>(null);
  const [isModalLoading, setIsModalLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // 챗봇에서 추천 장소 업데이트
  const handlePlacesUpdate = useCallback((newPlaces: PlaceResult[]) => {
    setPlaces(newPlaces);
    setSelectedId(null);
  }, []);

  // 카드/마커 선택 → 지도 중심 이동
  const handlePlaceSelect = useCallback((contentId: string) => {
    setSelectedId((prev) => (prev === contentId ? null : contentId));
  }, []);

  // 상세 모달 열기
  const handleDetailClick = useCallback(async (contentId: string) => {
    setIsModalOpen(true);
    setIsModalLoading(true);
    setModalPlace(null);
    try {
      const detail = await getPlaceDetail(contentId);
      setModalPlace(detail);
    } catch (err) {
      console.error("상세 정보 로드 실패:", err);
      setIsModalOpen(false);
    } finally {
      setIsModalLoading(false);
    }
  }, []);

  // 필터로 장소 검색
  const handleFilter = useCallback(async (filter: FilterState) => {
    if (!filter.region && !filter.keyword) return;
    setIsFilterLoading(true);
    try {
      const result = await searchPlaces({
        region: filter.region || undefined,
        keyword: filter.keyword || undefined,
        num_of_rows: 20,
      });

      // 실내/야외 클라이언트 사이드 필터
      let filtered = result.places;
      if (filter.placeType !== "all") {
        const indoorWords = ["실내", "카페", "박물관", "전시", "갤러리"];
        const outdoorWords = ["공원", "해변", "야외", "산", "숲", "광장", "해수욕"];
        filtered = result.places.filter((p) => {
          const text = `${p.title} ${p.address} ${p.reason || ""}`;
          if (filter.placeType === "indoor") {
            return indoorWords.some((w) => text.includes(w));
          } else {
            return outdoorWords.some((w) => text.includes(w));
          }
        });
      }
      setPlaces(filtered);
    } catch (err) {
      console.error("필터 검색 실패:", err);
    } finally {
      setIsFilterLoading(false);
    }
  }, []);

  return (
    <div className={styles.page}>
      {/* ── 헤더 ─────────────────────────────────── */}
      <header className={styles.header}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>🐾</span>
          <span className="text-gradient">펫 트래블</span>
        </div>
        <p className={styles.tagline}>반려동물과 함께하는 특별한 여행, AI가 찾아드립니다</p>
      </header>

      {/* ── 필터바 ───────────────────────────────── */}
      <div className={styles.filterWrap}>
        <FilterBar onFilter={handleFilter} isLoading={isFilterLoading} />
      </div>

      {/* ── 메인 본문 (지도 + 챗봇) ────────────── */}
      <main className={styles.main}>
        {/* 지도 */}
        <section className={styles.mapSection} aria-label="지도">
          {places.length === 0 && (
            <div className={styles.mapPlaceholder}>
              <span style={{ fontSize: "2.5rem" }}>🗺️</span>
              <p>챗봇에 질문하거나 필터를 선택하면<br />추천 장소가 지도에 표시됩니다</p>
            </div>
          )}
          <MapView
            places={places}
            selectedId={selectedId}
            onMarkerClick={(p) => handlePlaceSelect(p.contentId)}
          />
        </section>

        {/* 챗봇 */}
        <section className={styles.chatSection} aria-label="챗봇">
          <ChatPanel
            onPlacesUpdate={handlePlacesUpdate}
            onPlaceSelect={handlePlaceSelect}
          />
        </section>
      </main>

      {/* ── 추천 장소 카드 리스트 ─────────────── */}
      <section className={styles.listSection}>
        <PlaceList
          places={places}
          selectedId={selectedId}
          onSelect={handlePlaceSelect}
          onDetailClick={handleDetailClick}
        />
      </section>

      {/* ── 상세 모달 ──────────────────────────── */}
      {isModalOpen && (
        <PlaceDetailModal
          place={modalPlace}
          isLoading={isModalLoading}
          onClose={() => {
            setIsModalOpen(false);
            setModalPlace(null);
          }}
        />
      )}
    </div>
  );
}
