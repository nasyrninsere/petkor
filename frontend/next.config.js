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

  // API 프록시 - localhost일 때는 rewrite 비활성화 (Vercel 빌드 오류 방지)
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
    if (!apiUrl || apiUrl.includes("localhost")) {
      return [];
    }
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
