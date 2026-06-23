/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  async rewrites() {
    const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
    return [{ source: '/proxy/:path*', destination: `${apiBase}/:path*` }];
  },
};

export default nextConfig;
