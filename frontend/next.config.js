/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    // 한국관광공사 이미지 도메인 허용
    remotePatterns: [
      {
        protocol: "http",
        hostname: "tong.visitkorea.or.kr",
      },
      {
        protocol: "https",
        hostname: "tong.visitkorea.or.kr",
      },
      {
        protocol: "http",
        hostname: "**.visitkorea.or.kr",
      },
    ],
  },

  // API 프록시 (선택: 백엔드 URL이 환경변수로 관리될 때)
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
