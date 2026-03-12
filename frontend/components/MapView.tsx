"use client";

/**
 * 지도 뷰 컴포넌트 - Leaflet.js + OpenStreetMap
 * 이 파일은 page.tsx에서 dynamic({ ssr: false })로만 임포트되어야 합니다.
 */
import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { Map as LeafletMap, Marker } from "leaflet";
import type { PlaceResult } from "@/lib/types";

// webpack이 leaflet 기본 마커 이미지를 못 찾는 문제 해결
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

interface MapViewProps {
  places: PlaceResult[];
  selectedId?: string | null;
  onMarkerClick?: (place: PlaceResult) => void;
}

export default function MapView({ places, selectedId, onMarkerClick }: MapViewProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const markersRef = useRef<Marker[]>([]);

  // ── 지도 초기화 ──────────────────────────────
  useEffect(() => {
    if (mapRef.current || !mapContainerRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [36.5, 127.5],
      zoom: 7,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // ── 마커 업데이트 ────────────────────────────
  useEffect(() => {
    if (!mapRef.current) return;

    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    const valid = places.filter((p) => p.lat && p.lng);
    if (!valid.length) return;

    const bounds: [number, number][] = [];

    valid.forEach((place) => {
      const { lat, lng } = place;
      bounds.push([lat!, lng!]);

      const color = place.petAvailable ? "#6C63FF" : "#FF6B6B";
      const icon = L.divIcon({
        html: `<div style="width:36px;height:44px;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.4))">
          <svg xmlns="http://www.w3.org/2000/svg" width="36" height="44" viewBox="0 0 36 44">
            <ellipse cx="18" cy="40" rx="7" ry="3" fill="rgba(0,0,0,0.2)"/>
            <path d="M18 0C11.4 0 6 5.4 6 12c0 9 12 28 12 28S30 21 30 12C30 5.4 24.6 0 18 0z" fill="${color}"/>
            <circle cx="18" cy="12" r="7" fill="white" opacity="0.9"/>
            <text x="18" y="17" text-anchor="middle" font-size="10">🐾</text>
          </svg></div>`,
        className: "",
        iconSize: [36, 44],
        iconAnchor: [18, 44],
        popupAnchor: [0, -44],
      });

      const marker = L.marker([lat!, lng!], { icon });
      marker.bindPopup(`
        <div style="background:#1A1A2E;color:#F0F0FF;border:1px solid rgba(108,99,255,0.4);
          border-radius:10px;padding:10px 14px;min-width:160px;font-family:sans-serif;">
          <b style="font-size:13px">${place.title}</b>
          <div style="font-size:11px;color:#A0A0C0;margin:4px 0">📍 ${place.address}</div>
          <span style="font-size:11px;font-weight:600;color:${place.petAvailable ? "#4ECDC4" : "#FF6B6B"}">
            ${place.petAvailable ? "✅ 동반 가능" : "⚠️ 확인 필요"}
          </span>
        </div>`, { closeButton: true });

      marker.on("click", () => onMarkerClick?.(place));
      marker.addTo(mapRef.current!);
      markersRef.current.push(marker);
    });

    if (bounds.length) {
      mapRef.current.fitBounds(bounds, { padding: [40, 40] });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [places]);

  // ── 선택 장소로 이동 ─────────────────────────
  useEffect(() => {
    if (!mapRef.current || !selectedId) return;
    const place = places.find((p) => p.contentId === selectedId);
    if (place?.lat && place?.lng) {
      mapRef.current.flyTo([place.lat, place.lng], 13, { duration: 0.8 });
    }
  }, [selectedId, places]);

  return (
    <div
      id="leaflet-map"
      ref={mapContainerRef}
      style={{ width: "100%", height: "100%", borderRadius: "16px", overflow: "hidden" }}
    />
  );
}
