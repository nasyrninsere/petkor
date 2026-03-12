"use client";

/**
 * 추천 장소 리스트 (하단 카드 그리드)
 */
import type { PlaceResult } from "@/lib/types";
import PlaceCard from "./PlaceCard";
import styles from "./PlaceList.module.css";

interface PlaceListProps {
  places: PlaceResult[];
  selectedId?: string | null;
  onSelect: (contentId: string) => void;
  onDetailClick: (contentId: string) => void;
}

export default function PlaceList({
  places,
  selectedId,
  onSelect,
  onDetailClick,
}: PlaceListProps) {
  if (places.length === 0) return null;

  return (
    <section className={styles.section} aria-label="추천 장소 목록">
      <div className={styles.header}>
        <h2 className={styles.title}>
          📍 추천 장소 <span className={styles.count}>{places.length}곳</span>
        </h2>
      </div>
      <div className={styles.grid}>
        {places.map((place) => (
          <PlaceCard
            key={place.contentId}
            place={place}
            selected={selectedId === place.contentId}
            onClick={() => onSelect(place.contentId)}
            onDetailClick={() => onDetailClick(place.contentId)}
          />
        ))}
      </div>
    </section>
  );
}
