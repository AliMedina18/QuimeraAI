import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  outputFileTracingRoot: __dirname,
  allowedDevOrigins: ["*"],
  experimental: { reactCompiler: false },
  // ESLint v9 + eslint-config-next ahora trata `react-hooks/set-state-in-effect`
  // como error, lo que rompe `next build`. No son errores de tipos ni de runtime,
  // así que no bloqueamos el build de producción por esto (lint sigue corriendo
  // en `npm run lint` / CI).
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
