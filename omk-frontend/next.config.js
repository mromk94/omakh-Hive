/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Performance optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production', // Remove console.log in production
  },
  
  // Image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  
  // Webpack optimizations
  webpack: (config, { dev, isServer }) => {
    // Stub optional Node-only modules that leak into client bundles
    config.resolve = config.resolve || {}
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      'pino-pretty': false,
      '@react-native-async-storage/async-storage': false,
    }
    // Production optimizations
    if (!dev && !isServer) {
      // Code splitting optimization
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            // Vendor chunk for node_modules
            vendor: {
              name: 'vendor',
              chunks: 'all',
              test: /node_modules/,
              priority: 20,
            },
            // Common chunk for shared components
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              priority: 10,
              reuseExistingChunk: true,
              enforce: true,
            },
            // Separate chunks for large libraries
            react: {
              name: 'react',
              test: /[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/,
              chunks: 'all',
              priority: 30,
            },
            wagmi: {
              name: 'wagmi',
              test: /[\\/]node_modules[\\/](wagmi|viem|@rainbow-me)[\\/]/,
              chunks: 'all',
              priority: 25,
            },
          },
        },
      };
    }
    
    return config;
  },
  
  // Output optimization
  productionBrowserSourceMaps: false, // Disable source maps in production for smaller bundle
  
  // Compress pages
  compress: true,
  
  // Experimental features disabled to avoid missing optional deps during build
  
  // SWC minification (faster than Terser)
  swcMinify: true,
}

module.exports = nextConfig
