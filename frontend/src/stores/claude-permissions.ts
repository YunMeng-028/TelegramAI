/**
 * Claude Code 权限管理状态存储
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ClaudeCodeTool, ToolPermission } from '@/services/claude-code/types'

export const useClaudePermissionsStore = defineStore('claude-permissions', () => {
  // 工具权限映射
  const toolPermissions = ref<Map<ClaudeCodeTool, ToolPermission>>(new Map())
  
  // 全局权限规则
  const globalRules = ref({
    allow: [] as string[],
    deny: [] as string[]
  })
  
  // 初始化默认权限
  const initializePermissions = () => {
    const defaultPermissions: ToolPermission[] = [
      { tool: 'Read', allowed: true, description: '读取文件内容' },
      { tool: 'Grep', allowed: true, description: '搜索文件内容' },
      { tool: 'Glob', allowed: true, description: '文件模式匹配' },
      { tool: 'LS', allowed: true, description: '列出文件目录' },
      { tool: 'TodoWrite', allowed: true, description: '任务管理' },
      { tool: 'Task', allowed: true, description: '执行复杂任务' },
      { tool: 'WebSearch', allowed: true, description: '网络搜索' },
      { tool: 'WebFetch', allowed: false, description: '获取网页内容' },
      { tool: 'Bash', allowed: false, description: '执行系统命令' },
      { tool: 'Write', allowed: false, description: '写入文件' },
      { tool: 'Edit', allowed: false, description: '编辑文件' },
      { tool: 'MultiEdit', allowed: false, description: '批量编辑文件' },
      { tool: 'NotebookRead', allowed: true, description: '读取Jupyter笔记本' },
      { tool: 'NotebookEdit', allowed: false, description: '编辑Jupyter笔记本' }
    ]
    
    defaultPermissions.forEach(perm => {
      toolPermissions.value.set(perm.tool, perm)
    })
  }
  
  // 获取所有权限
  const getAllPermissions = computed(() => {
    return Array.from(toolPermissions.value.values())
  })
  
  // 获取允许的工具
  const getAllowedTools = computed(() => {
    return Array.from(toolPermissions.value.entries())
      .filter(([_, perm]) => perm.allowed)
      .map(([tool]) => tool)
  })
  
  // 获取拒绝的工具
  const getDeniedTools = computed(() => {
    return Array.from(toolPermissions.value.entries())
      .filter(([_, perm]) => !perm.allowed)
      .map(([tool]) => tool)
  })
  
  // 设置工具权限
  const setToolPermission = (tool: ClaudeCodeTool, allowed: boolean, restrictions?: string[]) => {
    const existing = toolPermissions.value.get(tool)
    if (existing) {
      existing.allowed = allowed
      if (restrictions) {
        existing.restrictions = restrictions
      }
    } else {
      toolPermissions.value.set(tool, {
        tool,
        allowed,
        restrictions,
        description: ''
      })
    }
  }
  
  // 批量更新权限
  const updatePermissions = (permissions: ToolPermission[]) => {
    permissions.forEach(perm => {
      toolPermissions.value.set(perm.tool, perm)
    })
  }
  
  // 添加全局规则
  const addGlobalRule = (type: 'allow' | 'deny', rule: string) => {
    if (!globalRules.value[type].includes(rule)) {
      globalRules.value[type].push(rule)
    }
  }
  
  // 移除全局规则
  const removeGlobalRule = (type: 'allow' | 'deny', rule: string) => {
    const index = globalRules.value[type].indexOf(rule)
    if (index > -1) {
      globalRules.value[type].splice(index, 1)
    }
  }
  
  // 检查工具是否允许
  const isToolAllowed = (tool: ClaudeCodeTool, command?: string): boolean => {
    const permission = toolPermissions.value.get(tool)
    if (!permission) return false
    
    // 基础权限检查
    if (!permission.allowed) return false
    
    // 如果有命令，检查全局规则
    if (command) {
      const fullCommand = `${tool}(${command})`
      
      // 检查拒绝规则
      for (const denyRule of globalRules.value.deny) {
        if (matchRule(fullCommand, denyRule)) {
          return false
        }
      }
      
      // 检查允许规则
      for (const allowRule of globalRules.value.allow) {
        if (matchRule(fullCommand, allowRule)) {
          return true
        }
      }
    }
    
    return permission.allowed
  }
  
  // 规则匹配
  const matchRule = (command: string, rule: string): boolean => {
    // 支持通配符匹配
    const regex = new RegExp('^' + rule.replace(/\*/g, '.*') + '$')
    return regex.test(command)
  }
  
  // 导出权限配置
  const exportConfig = () => {
    return {
      permissions: Array.from(toolPermissions.value.values()),
      globalRules: globalRules.value
    }
  }
  
  // 导入权限配置
  const importConfig = (config: any) => {
    if (config.permissions) {
      toolPermissions.value.clear()
      config.permissions.forEach((perm: ToolPermission) => {
        toolPermissions.value.set(perm.tool, perm)
      })
    }
    
    if (config.globalRules) {
      globalRules.value = config.globalRules
    }
  }
  
  // 应用场景预设
  const applyScenarioPreset = (scenario: 'readonly' | 'contentGeneration' | 'development') => {
    const presets = {
      readonly: {
        allowed: ['Read', 'Grep', 'Glob', 'LS', 'WebSearch'],
        denied: ['Write', 'Edit', 'Bash', 'MultiEdit', 'WebFetch'],
        rules: {
          allow: [],
          deny: ['*']
        }
      },
      contentGeneration: {
        allowed: ['TodoWrite', 'Task', 'WebSearch', 'Read', 'WebFetch'],
        denied: ['Bash', 'Write', 'Edit', 'MultiEdit'],
        rules: {
          allow: [],
          deny: ['Bash(*)', 'Write(*)', 'Edit(*)']
        }
      },
      development: {
        allowed: ['Read', 'Write', 'Edit', 'MultiEdit', 'Grep', 'Glob', 'LS', 'TodoWrite', 'Task', 'WebSearch', 'WebFetch'],
        denied: [],
        rules: {
          allow: ['Bash(npm*)', 'Bash(yarn*)', 'Bash(git*)', 'Bash(python*)', 'Bash(node*)'],
          deny: ['Bash(rm -rf*)', 'Bash(sudo*)', 'Bash(chmod 777*)', 'Bash(curl * | sh)']
        }
      }
    }
    
    const preset = presets[scenario]
    if (!preset) return
    
    // 更新工具权限
    toolPermissions.value.forEach((perm, tool) => {
      if (preset.allowed.includes(tool)) {
        perm.allowed = true
      } else if (preset.denied.includes(tool)) {
        perm.allowed = false
      }
    })
    
    // 更新全局规则
    globalRules.value = { ...preset.rules }
  }
  
  // 初始化
  initializePermissions()
  
  return {
    toolPermissions,
    globalRules,
    getAllPermissions,
    getAllowedTools,
    getDeniedTools,
    setToolPermission,
    updatePermissions,
    addGlobalRule,
    removeGlobalRule,
    isToolAllowed,
    exportConfig,
    importConfig,
    applyScenarioPreset
  }
})