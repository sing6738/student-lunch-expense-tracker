import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'
import fs from 'node:fs'
import path from 'node:path'

function cleanStaleAssets() {
  return {
    name: 'clean-stale-assets',
    buildStart() {
      const currentDir = typeof import.meta.dirname !== 'undefined' ? import.meta.dirname : fileURLToPath(new URL('.', import.meta.url))
      const staticDir = path.resolve(currentDir, '../static')
      const assetsDir = path.join(staticDir, 'assets')
      // Remove stale assets bundle directory so deleted/re-hashed chunks don't accumulate
      if (fs.existsSync(assetsDir)) {
        fs.rmSync(assetsDir, { recursive: true, force: true })
      }
      // Remove stale workbox scripts in static directory
      if (fs.existsSync(staticDir)) {
        const files = fs.readdirSync(staticDir)
        for (const file of files) {
          if (file.startsWith('workbox-') && file.endsWith('.js')) {
            try {
              fs.unlinkSync(path.join(staticDir, file))
            } catch {
              // ignore
            }
          }
        }
      }
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    cleanStaleAssets(),
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'favicon.svg', 'apple-touch-icon.png', 'masked-icon.svg', 'pwa-192x192.png', 'pwa-512x512.png'],
      manifest: {
        name: 'Lunch Expense Tracker',
        short_name: 'LunchTrack',
        description: 'ติดตามค่าอาหารกลางวันรายวัน สำหรับนักเรียนไทย',
        theme_color: '#1B4D3E',
        background_color: '#FAF8F5',
        display: 'standalone',
        orientation: 'portrait-primary',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ],
        categories: ['finance', 'productivity', 'education'],
        lang: 'th-TH',
        dir: 'ltr'
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^\/api\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 // 24 hours
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: true,
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: '../static',
    emptyOutDir: false,
    rollupOptions: {
      output: {
        entryFileNames: `assets/[name]-[hash].js`,
        chunkFileNames: `assets/[name]-[hash].js`,
        assetFileNames: `assets/[name]-[hash].[ext]`
      }
    }
  }
})
