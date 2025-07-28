import js from '@eslint/js'
import typescript from '@typescript-eslint/eslint-plugin'
import typescriptParser from '@typescript-eslint/parser'
import vue from 'eslint-plugin-vue'
import vueParser from 'vue-eslint-parser'
import prettier from '@vue/eslint-config-prettier'

export default [
  js.configs.recommended,
  
  // TypeScript配置
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        project: './tsconfig.json'
      }
    },
    plugins: {
      '@typescript-eslint': typescript
    },
    rules: {
      ...typescript.configs.recommended.rules,
      '@typescript-eslint/no-unused-vars': 'error',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-non-null-assertion': 'warn'
    }
  },
  
  // Vue配置
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        parser: typescriptParser,
        extraFileExtensions: ['.vue']
      }
    },
    plugins: {
      vue,
      '@typescript-eslint': typescript
    },
    rules: {
      ...vue.configs['vue3-recommended'].rules,
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'warn',
      'vue/require-default-prop': 'off',
      'vue/require-explicit-emits': 'error',
      'vue/component-definition-name-casing': ['error', 'PascalCase'],
      'vue/component-name-in-template-casing': ['error', 'PascalCase'],
      'vue/custom-event-name-casing': ['error', 'camelCase'],
      'vue/define-macros-order': ['error', {
        order: ['defineProps', 'defineEmits']
      }],
      'vue/html-self-closing': ['error', {
        html: {
          void: 'never',
          normal: 'always',
          component: 'always'
        },
        svg: 'always',
        math: 'always'
      }],
      'vue/max-attributes-per-line': ['error', {
        singleline: 3,
        multiline: 1
      }]
    }
  },
  
  // JavaScript配置
  {
    files: ['**/*.js', '**/*.mjs', '**/*.cjs'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module'
    },
    rules: {
      'no-unused-vars': 'error',
      'no-console': 'warn',
      'no-debugger': 'warn'
    }
  },
  
  // Electron主进程配置
  {
    files: ['frontend/electron/**/*.js', 'frontend/electron/**/*.ts'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        __dirname: 'readonly',
        __filename: 'readonly',
        Buffer: 'readonly',
        process: 'readonly',
        global: 'readonly'
      }
    },
    rules: {
      'no-console': 'off' // Electron主进程允许console
    }
  },
  
  // 通用规则
  {
    rules: {
      'no-var': 'error',
      'prefer-const': 'error',
      'prefer-arrow-callback': 'error',
      'object-shorthand': 'error',
      'quote-props': ['error', 'as-needed'],
      'no-array-constructor': 'error',
      'no-new-object': 'error',
      'no-prototype-builtins': 'error',
      'no-iterator': 'error',
      'no-restricted-syntax': [
        'error',
        'ForInStatement',
        'LabeledStatement',
        'WithStatement'
      ],
      'space-before-function-paren': ['error', {
        anonymous: 'always',
        named: 'never',
        asyncArrow: 'always'
      }],
      'keyword-spacing': 'error',
      'space-infix-ops': 'error',
      'eol-last': 'error',
      'newline-per-chained-call': ['error', { ignoreChainWithDepth: 4 }],
      'no-whitespace-before-property': 'error',
      'padded-blocks': ['error', 'never'],
      'space-in-parens': ['error', 'never'],
      'array-bracket-spacing': ['error', 'never'],
      'object-curly-spacing': ['error', 'always'],
      'comma-style': ['error', 'last'],
      'comma-dangle': ['error', 'never'],
      'semi': ['error', 'never'],
      'quotes': ['error', 'single', { avoidEscape: true }],
      'prefer-template': 'error',
      'template-curly-spacing': 'error',
      'no-eval': 'error',
      'no-useless-escape': 'error'
    }
  },
  
  // 忽略文件
  {
    ignores: [
      'node_modules/**',
      'dist/**',
      'dist-electron/**',
      'out/**',
      'backend/**',
      '**/*.d.ts',
      'frontend/types/auto-imports.d.ts',
      'frontend/types/components.d.ts',
      '.eslintrc-auto-import.json'
    ]
  }
]