module.exports = {
  // 测试环境
  testEnvironment: 'jsdom',
  
  // 测试文件匹配模式
  testMatch: [
    '<rootDir>/frontend/**/__tests__/**/*.(js|jsx|ts|tsx)',
    '<rootDir>/frontend/**/?(*.)(spec|test).(js|jsx|ts|tsx)'
  ],
  
  // 模块路径映射
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/frontend/src/$1',
    '^~/(.*)$': '<rootDir>/frontend/$1'
  },
  
  // 转换配置
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.(js|jsx)$': 'babel-jest',
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },
  
  // 文件扩展名
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx', 'vue', 'json'],
  
  // 安装文件
  setupFilesAfterEnv: ['<rootDir>/frontend/tests/setup.ts'],
  
  // 覆盖率配置
  collectCoverage: true,
  collectCoverageFrom: [
    'frontend/src/**/*.{js,jsx,ts,tsx,vue}',
    '!frontend/src/**/*.d.ts',
    '!frontend/src/**/index.{js,ts}',
    '!frontend/src/main.ts',
    '!frontend/src/types/**/*',
    '!**/node_modules/**',
    '!**/vendor/**'
  ],
  coverageDirectory: '<rootDir>/coverage',
  coverageReporters: ['text', 'lcov', 'html', 'json'],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  },
  
  // 忽略模式
  testPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/dist/',
    '<rootDir>/backend/'
  ],
  
  // 模块忽略模式
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$|@vue/test-utils|@testing-library))'
  ],
  
  // 全局变量
  globals: {
    'ts-jest': {
      useESM: true,
      tsconfig: {
        module: 'esnext'
      }
    }
  }
}