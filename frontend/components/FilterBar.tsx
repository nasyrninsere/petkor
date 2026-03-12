"use client";

/**
 * 필터 바 컴포넌트
 * - 지역 선택, 키워드 검색, 실내/야외 필터
 * - 변경 시 콜백으로 부모에 알림
 */
import { useState } from "react";
import type { FilterState } from "@/lib/types";
import styles from "./FilterBar.module.css";

interface FilterBarProps {
  onFilter: (filter: FilterState) => void;
  isLoading?: boolean;
}

const REGIONS = [
  "전체", "서울", "경기", "강원", "인천",
  "부산", "경남", "제주", "전남", "전북",
  "충남", "충북", "경북", "대구", "광주", "대전",
];

const PLACE_TYPES: { value: FilterState["placeType"]; label: string }[] = [
  { value: "all", label: "전체" },
  { value: "indoor", label: "🏠 실내" },
  { value: "outdoor", label: "🌿 야외" },
];

export default function FilterBar({ onFilter, isLoading }: FilterBarProps) {
  const [filter, setFilter] = useState<FilterState>({
    region: "",
    keyword: "",
    placeType: "all",
  });

  const update = (partial: Partial<FilterState>) => {
    const next = { ...filter, ...partial };
    setFilter(next);
    onFilter(next);
  };

  return (
    <div className={styles.bar} role="search" aria-label="장소 필터">
      {/* 지역 */}
      <div className={styles.regions}>
        {REGIONS.map((r) => (
          <button
            key={r}
            className={`${styles.regionBtn} ${filter.region === (r === "전체" ? "" : r) ? styles.active : ""}`}
            onClick={() => update({ region: r === "전체" ? "" : r })}
            disabled={isLoading}
            aria-pressed={filter.region === (r === "전체" ? "" : r)}
          >
            {r}
          </button>
        ))}
      </div>

      {/* 키워드 + 실내/야외 */}
      <div className={styles.controls}>
        <input
          type="text"
          id="filter-keyword"
          className={styles.keywordInput}
          placeholder="🔍 키워드 (예: 공원, 카페)"
          value={filter.keyword}
          onChange={(e) => update({ keyword: e.target.value })}
          disabled={isLoading}
        />

        <div className={styles.typeGroup}>
          {PLACE_TYPES.map((pt) => (
            <button
              key={pt.value}
              className={`${styles.typeBtn} ${filter.placeType === pt.value ? styles.active : ""}`}
              onClick={() => update({ placeType: pt.value })}
              disabled={isLoading}
            >
              {pt.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
