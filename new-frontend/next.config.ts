import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  async rewrites() {
    return [
      { source: "/kingdom/:path*", destination: "http://localhost:3001/kingdom/:path*" },
    ];
  },
};

export default nextConfig;
