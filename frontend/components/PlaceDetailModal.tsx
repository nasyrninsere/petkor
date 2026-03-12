"use client";

/**
 * 장소 상세 모달
 * - 장소 상세 정보 전체 표시
 * - 이미지 갤러리
 * - 반려동물 정보 체크리스트
 * - ESC 키 닫기
 */
import { useEffect, useCallback } from "react";
import Image from "next/image";
import type { PlaceDetail } from "@/lib/types";
import styles from "./PlaceDetailModal.module.css";

interface PlaceDetailModalProps {
  place: PlaceDetail | null;
  onClose: () => void;
  isLoading?: boolean;
}

export default function PlaceDetailModal({ place, onClose, isLoading }: PlaceDetailModalProps) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    if (place) document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [handleKeyDown, place]);

  if (!place && !isLoading) return null;

  return (
    <div
      className={styles.overlay}
      onClick={(e) => e.target === e.currentTarget && onClose()}
      role="dialog"
      aria-modal="true"
      aria-label="장소 상세 정보"
    >
      <div className={styles.modal}>
        {/* 닫기 버튼 */}
        <button
          id="modal-close-btn"
          className={styles.closeBtn}
          onClick={onClose}
          aria-label="닫기"
        >
          ✕
        </button>

        {isLoading ? (
          <div className={styles.loadingState}>
            <div className="spinner" style={{ width: 36, height: 36, borderWidth: 3 }} />
            <p>장소 정보를 불러오는 중...</p>
          </div>
        ) : place ? (
          <div className={styles.content}>
            {/* 헤더 이미지 */}
            <div className={styles.heroWrap}>
              {place.imageUrl ? (
                <Image
                  src={place.imageUrl}
                  alt={place.title}
                  fill
                  sizes="(max-width: 768px) 100vw, 800px"
                  style={{ objectFit: "cover" }}
                  priority
                />
              ) : (
                <div className={styles.heroPlaceholder}>🐾</div>
              )}
              <div className={styles.heroOverlay}>
                <h1 className={styles.heroTitle}>{place.title}</h1>
                <div className={styles.heroAddress}>📍 {place.address}</div>
                <span className={place.petAvailable ? "badge-pet-ok" : "badge-pet-check"}>
                  {place.petAvailable ? "✅ 반려동물 동반 가능" : "⚠️ 동반 조건 확인 필요"}
                </span>
              </div>
            </div>

            {/* 본문 */}
            <div className={styles.body}>
              {/* 기본 소개 */}
              {place.overview && (
                <section className={styles.section}>
                  <h2 className={styles.sectionTitle}>📖 기본 소개</h2>
                  <p className={styles.overview}>{place.overview}</p>
                </section>
              )}

              {/* 방문 정보 */}
              <section className={styles.section}>
                <h2 className={styles.sectionTitle}>ℹ️ 방문 정보</h2>
                <div className={styles.infoGrid}>
                  {place.tel && (
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>📞 전화</span>
                      <span>{place.tel}</span>
                    </div>
                  )}
                  {place.useTime && (
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>⏰ 운영시간</span>
                      <span>{place.useTime}</span>
                    </div>
                  )}
                  {place.restDate && (
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>🚫 휴무일</span>
                      <span>{place.restDate}</span>
                    </div>
                  )}
                  {place.parking && (
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>🅿️ 주차</span>
                      <span>{place.parking}</span>
                    </div>
                  )}
                  {place.homepage && (
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>🌐 홈페이지</span>
                      <a
                        href={place.homepage}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.link}
                      >
                        바로가기 →
                      </a>
                    </div>
                  )}
                </div>
              </section>

              {/* 반려동물 체크포인트 */}
              <section className={styles.section}>
                <h2 className={styles.sectionTitle}>🐾 반려동물 동반 안내</h2>
                <div className={styles.petInfoBox}>
                  {[
                    { label: "동반 정보", value: place.petInfo },
                    { label: "⚠️ 주의사항", value: place.caution },
                    { label: "🚷 제한사항", value: place.restrictions },
                  ].map(({ label, value }) =>
                    value ? (
                      <div key={label} className={styles.petInfoRow}>
                        <span className={styles.petInfoLabel}>{label}</span>
                        <span className={styles.petInfoValue}>{value}</span>
                      </div>
                    ) : null
                  )}

                  {place.checkpoints && (
                    <div className={styles.checkpoints}>
                      <div className={styles.petInfoLabel}>📋 체크포인트</div>
                      <pre className={styles.checkpointText}>{place.checkpoints}</pre>
                    </div>
                  )}

                  {!place.petInfo && !place.caution && !place.restrictions && (
                    <p className={styles.noPetInfo}>
                      반려동물 상세 정보가 없습니다. 방문 전 직접 확인하세요.
                    </p>
                  )}
                </div>
              </section>

              {/* 추가 이미지 */}
              {place.images && place.images.length > 0 && (
                <section className={styles.section}>
                  <h2 className={styles.sectionTitle}>🖼️ 사진</h2>
                  <div className={styles.gallery}>
                    {place.images.slice(0, 6).map((img, i) => (
                      <div key={i} className={styles.galleryItem}>
                        <Image
                          src={img}
                          alt={`${place.title} 이미지 ${i + 1}`}
                          fill
                          sizes="200px"
                          style={{ objectFit: "cover" }}
                        />
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
