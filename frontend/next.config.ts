import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Exportacion estatica para Firebase Hosting
  // Cambia a 'standalone' si despliegas en Cloud Run en vez de Firebase
  output: 'export',
  trailingSlash: true,
  images: { unoptimized: true },
};

export default nextConfig;
