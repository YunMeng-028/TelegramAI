/**
 * Claude Code 工具配置和管理
 */

import type { ClaudeCodeTool, ClaudeCodeOptions } from './types';

/**
 * 工具权限配置
 */
export interface ToolPermission {
  tool: ClaudeCodeTool;
  allowed: boolean;
  restrictions?: string[];
  description?: string;
}

/**
 * 默认工具配置
 */
export const DEFAULT_TOOL_PERMISSIONS: ToolPermission[] = [
  {
    tool: 'Read',
    allowed: true,
    description: '读取文件内容'
  },
  {
    tool: 'Grep',
    allowed: true,
    description: '搜索文件内容'
  },
  {
    tool: 'Glob',
    allowed: true,
    description: '文件模式匹配'
  },
  {
    tool: 'TodoWrite',
    allowed: true,
    description: '任务管理'
  },
  {
    tool: 'Task',
    allowed: true,
    description: '执行复杂任务'
  },
  {
    tool: 'WebSearch',
    allowed: true,
    description: '网络搜索'
  },
  {
    tool: 'WebFetch',
    allowed: false,
    description: '获取网页内容（需要额外权限）'
  },
  {
    tool: 'Bash',
    allowed: false,
    description: '执行系统命令（需要额外权限）'
  },
  {
    tool: 'Write',
    allowed: false,
    description: '写入文件（需要额外权限）'
  },
  {
    tool: 'Edit',
    allowed: false,
    description: '编辑文件（需要额外权限）'
  }
];

/**
 * 工具管理器
 */
export class ToolManager {
  private permissions: Map<ClaudeCodeTool, ToolPermission>;
  
  constructor(customPermissions?: ToolPermission[]) {
    this.permissions = new Map();
    
    // 加载默认权限
    DEFAULT_TOOL_PERMISSIONS.forEach(perm => {
      this.permissions.set(perm.tool, perm);
    });
    
    // 覆盖自定义权限
    customPermissions?.forEach(perm => {
      this.permissions.set(perm.tool, perm);
    });
  }
  
  /**
   * 获取允许的工具列表
   */
  getAllowedTools(): ClaudeCodeTool[] {
    return Array.from(this.permissions.entries())
      .filter(([_, perm]) => perm.allowed)
      .map(([tool]) => tool);
  }
  
  /**
   * 检查工具是否允许
   */
  isToolAllowed(tool: ClaudeCodeTool): boolean {
    return this.permissions.get(tool)?.allowed || false;
  }
  
  /**
   * 设置工具权限
   */
  setToolPermission(tool: ClaudeCodeTool, allowed: boolean, restrictions?: string[]): void {
    const existing = this.permissions.get(tool) || { tool, allowed: false };
    this.permissions.set(tool, {
      ...existing,
      allowed,
      restrictions
    });
  }
  
  /**
   * 构建Claude Code选项
   */
  buildOptions(baseOptions?: ClaudeCodeOptions): ClaudeCodeOptions {
    const allowedTools = this.getAllowedTools();
    
    // 构建权限规则
    const permissions: ClaudeCodeOptions['permissions'] = {
      allow: [],
      deny: []
    };
    
    this.permissions.forEach((perm, tool) => {
      if (perm.allowed) {
        if (perm.restrictions?.length) {
          // 有限制的允许
          perm.restrictions.forEach(restriction => {
            permissions.allow?.push(`${tool}(${restriction})`);
          });
        } else {
          // 完全允许
          permissions.allow?.push(tool);
        }
      } else {
        // 拒绝
        permissions.deny?.push(tool);
      }
    });
    
    return {
      ...baseOptions,
      allowedTools,
      permissions
    };
  }
  
  /**
   * 导出权限配置
   */
  exportPermissions(): ToolPermission[] {
    return Array.from(this.permissions.values());
  }
  
  /**
   * 导入权限配置
   */
  importPermissions(permissions: ToolPermission[]): void {
    permissions.forEach(perm => {
      this.permissions.set(perm.tool, perm);
    });
  }
}

/**
 * 创建针对特定场景的工具配置
 */
export const SCENARIO_PRESETS = {
  /**
   * 只读分析场景
   */
  readonly: {
    allowedTools: ['Read', 'Grep', 'Glob', 'LS', 'WebSearch'] as ClaudeCodeTool[],
    permissions: {
      deny: ['Write', 'Edit', 'Bash', 'MultiEdit']
    }
  },
  
  /**
   * 内容生成场景
   */
  contentGeneration: {
    allowedTools: ['TodoWrite', 'Task', 'WebSearch', 'Read'] as ClaudeCodeTool[],
    permissions: {
      allow: ['WebFetch'],
      deny: ['Bash', 'Write', 'Edit']
    }
  },
  
  /**
   * 完整开发场景
   */
  development: {
    allowedTools: [
      'Read', 'Write', 'Edit', 'MultiEdit',
      'Grep', 'Glob', 'LS',
      'TodoWrite', 'Task',
      'WebSearch', 'WebFetch'
    ] as ClaudeCodeTool[],
    permissions: {
      allow: ['Bash(npm*)', 'Bash(yarn*)', 'Bash(git*)'],
      deny: ['Bash(rm*)', 'Bash(sudo*)']
    }
  }
};

/**
 * 获取场景预设
 */
export function getScenarioPreset(scenario: keyof typeof SCENARIO_PRESETS): ClaudeCodeOptions {
  return SCENARIO_PRESETS[scenario];
}