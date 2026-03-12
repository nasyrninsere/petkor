/**
 * layout.tsx - 카카오맵 SDK는 MapView에서 직접 로드하므로 여기서 제거
 */
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "🐾 펫 트래블 | 반려동물 동반여행 추천",
  description: "반려동물과 함께 떠나는 여행, AI가 최적의 여행지를 추천해 드립니다.",
  keywords: ["반려동물여행", "펫트래블", "강아지여행", "고양이여행", "반려견동반"],
  openGraph: {
    title: "🐾 펫 트래블 | 반려동물 동반여행 추천",
    description: "AI 챗봇이 반려동물과 함께 갈 수 있는 최고의 여행지를 추천해 드립니다.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
