import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'dist/',
        'dist-electron/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData.ts',
        'frontend/electron/**',
        'frontend/types/**',
        'frontend/src/main.ts',
        '**/index.{js,ts}',
        '**/__tests__/**',
        '**/*.test.*',
        '**/*.spec.*'
      ],
      thresholds: {
        global: {
          branches: 70,
          functions: 70,
          lines: 70,
          statements: 70
        }
      },
      all: true,
      include: ['frontend/src/**/*.{js,ts,vue}']
    },
    include: ['frontend/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', '.idea', '.git', '.cache'],
    testTimeout: 20000,
    hookTimeout: 20000
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./frontend/src', import.meta.url)),
      '~': fileURLToPath(new URL('./frontend', import.meta.url))
    }
  }
})