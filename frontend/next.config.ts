import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  outputFileTracingRoot: __dirname,
  allowedDevOrigins: ["*"],
  experimental: { reactCompiler: false },
};

export default nextConfig;
