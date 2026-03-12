"use client";

/**
 * 장소 카드 컴포넌트
 * - compact 모드: 챗봇 말풍선 속 작은 카드
 * - 일반 모드: 하단 리스트용 큰 카드
 * - 클릭 시 선택 + 지도 중심 이동
 */
import Image from "next/image";
import type { PlaceResult } from "@/lib/types";
import styles from "./PlaceCard.module.css";

interface PlaceCardProps {
  place: PlaceResult;
  compact?: boolean;
  selected?: boolean;
  onClick?: () => void;
  onDetailClick?: () => void;
}

export default function PlaceCard({
  place,
  compact = false,
  selected = false,
  onClick,
  onDetailClick,
}: PlaceCardProps) {
  return (
    <div
      className={`${styles.card} ${compact ? styles.compact : styles.full} ${selected ? styles.selected : ""}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && onClick?.()}
      aria-label={`${place.title} 카드`}
    >
      {/* 이미지 */}
      {!compact && (
        <div className={styles.imageWrap}>
          {place.imageUrl ? (
            <Image
              src={place.imageUrl}
              alt={place.title}
              fill
              sizes="(max-width: 768px) 100vw, 300px"
              style={{ objectFit: "cover" }}
              onError={(e) => {
                (e.target as HTMLImageElement).src = "/placeholder-pet.svg";
              }}
            />
          ) : (
            <div className={styles.imagePlaceholder}>🐾</div>
          )}
          <div className={styles.imageOverlay} />
        </div>
      )}

      {/* 컨텐츠 */}
      <div className={styles.content}>
        {compact && place.imageUrl && (
          <div className={styles.compactThumb}>
            <Image
              src={place.imageUrl}
              alt={place.title}
              fill
              sizes="56px"
              style={{ objectFit: "cover" }}
            />
          </div>
        )}

        <div className={styles.info}>
          <div className={styles.titleRow}>
            <div className={styles.title}>{place.title}</div>
            <span className={place.petAvailable ? "badge-pet-ok" : "badge-pet-check"}>
              {place.petAvailable ? "✅ 동반 가능" : "⚠️ 확인 필요"}
            </span>
          </div>

          <div className={styles.address}>📍 {place.address || "주소 정보 없음"}</div>

          {place.reason && (
            <div className={styles.reason}>{place.reason}</div>
          )}

          {!compact && place.caution && (
            <div className={styles.caution}>⚠️ {place.caution}</div>
          )}

          {!compact && (
            <button
              id={`detail-btn-${place.contentId}`}
              className={styles.detailBtn}
              onClick={(e) => {
                e.stopPropagation();
                onDetailClick?.();
              }}
            >
              상세보기 →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
