// 性能测试配置
module.exports = {
  // Lighthouse CI配置
  ci: {
    collect: {
      url: ['http://localhost:5173'],
      numberOfRuns: 3,
      settings: {
        chromeFlags: '--no-sandbox --disable-dev-shm-usage'
      }
    },
    assert: {
      assertions: {
        'categories:performance': ['warn', { minScore: 0.8 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.8 }],
        'categories:seo': ['warn', { minScore: 0.8 }]
      }
    },
    upload: {
      target: 'temporary-public-storage'
    }
  },
  
  // Web Vitals阈值
  vitals: {
    LCP: 2500,  // Largest Contentful Paint
    FID: 100,   // First Input Delay
    CLS: 0.1,   // Cumulative Layout Shift
    FCP: 1800,  // First Contentful Paint
    TTFB: 800   // Time to First Byte
  },
  
  // Bundle分析配置
  bundle: {
    analyzer: {
      analyzerMode: 'static',
      reportFilename: 'bundle-report.html',
      openAnalyzer: false
    },
    maxAssetSize: 512000,      // 512KB
    maxEntrypointSize: 512000  // 512KB
  },
  
  // 内存使用监控
  memory: {
    heapSizeLimit: 1024 * 1024 * 512, // 512MB
    checkInterval: 30000,              // 30s
    gcThreshold: 0.8                   // 80%
  },
  
  // API性能测试
  api: {
    baseURL: 'http://localhost:8000',
    timeout: 5000,
    concurrency: 10,
    requests: 100,
    endpoints: [
      { path: '/api/v1/health', method: 'GET' },
      { path: '/api/v1/accounts', method: 'GET' },
      { path: '/api/v1/stats/accounts/test', method: 'GET' }
    ]
  }
}