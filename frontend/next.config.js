// Enable bundle analyzer when ANALYZE env var is set
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true'
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Produce .next/standalone for minimal runtime image
  output: 'standalone',
  outputFileTracingRoot: require('path').join(__dirname, '..'),
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
  typescript: {
    // !! WARN !!
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    // !! WARN !!
    ignoreBuildErrors: true,
  },
  images: {
    domains: ['localhost', 'i.scdn.co', 'images.unsplash.com'],
  },
  modularizeImports: {
    'lucide-react': {
      transform: 'lucide-react/dist/esm/icons/{{member}}',
      skipDefaultConversion: true,
    },
  },
  typedRoutes: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        // Use internal URL inside Docker (service name), fallback to localhost for local dev
        destination: `${process.env.API_INTERNAL_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
};

module.exports = withBundleAnalyzer(nextConfig);
