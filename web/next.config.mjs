/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/unified/:path*',
        // This destination is now targeting the backend service within the Docker network
        destination: 'http://backend:8000/unified/:path*',
      },
    ];
  },
};

export default nextConfig;
