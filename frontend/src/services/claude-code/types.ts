/**
 * Claude Code SDK 类型定义
 */

export interface ClaudeCodeOptions {
  /**
   * 最大交互轮次
   */
  maxTurns?: number;
  
  /**
   * 系统提示词
   */
  systemPrompt?: string;
  
  /**
   * 允许使用的工具列表
   */
  allowedTools?: ClaudeCodeTool[];
  
  /**
   * 权限配置
   */
  permissions?: {
    allow?: string[];
    deny?: string[];
  };
  
  /**
   * 温度参数
   */
  temperature?: number;
  
  /**
   * 输出格式
   */
  outputFormat?: 'text' | 'json' | 'stream';
  
  /**
   * API密钥
   */
  apiKey?: string;
  
  /**
   * 超时时间（毫秒）
   */
  timeout?: number;
}

export type ClaudeCodeTool = 
  | 'Bash'
  | 'Edit'
  | 'Glob'
  | 'Grep'
  | 'LS'
  | 'MultiEdit'
  | 'NotebookEdit'
  | 'NotebookRead'
  | 'Read'
  | 'Task'
  | 'TodoWrite'
  | 'WebFetch'
  | 'WebSearch'
  | 'Write';

export interface ClaudeCodeMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  toolCalls?: ToolCall[];
  timestamp?: number;
}

export interface ToolCall {
  id: string;
  tool: ClaudeCodeTool;
  arguments: Record<string, any>;
  result?: any;
}

export interface ClaudeCodeResponse {
  messages: ClaudeCodeMessage[];
  status: 'success' | 'error' | 'streaming';
  error?: string;
  metadata?: {
    turnsUsed: number;
    tokensUsed: number;
    duration: number;
  };
}

export interface ClaudeCodeContext {
  /**
   * 会话ID
   */
  sessionId: string;
  
  /**
   * 用户信息
   */
  user?: {
    id: string;
    name: string;
    preferences?: Record<string, any>;
  };
  
  /**
   * 对话历史
   */
  history?: ClaudeCodeMessage[];
  
  /**
   * 上下文数据
   */
  contextData?: Record<string, any>;
}

export interface ClaudeCodeConfig {
  /**
   * API端点
   */
  endpoint?: string;
  
  /**
   * 默认选项
   */
  defaultOptions?: ClaudeCodeOptions;
  
  /**
   * 重试配置
   */
  retry?: {
    maxAttempts: number;
    backoffMs: number;
  };
  
  /**
   * 日志级别
   */
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

export interface TaskResult {
  taskId: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  result?: any;
  error?: string;
  startTime: number;
  endTime?: number;
}

export interface TodoItem {
  id: string;
  content: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'high' | 'medium' | 'low';
  createdAt: number;
  updatedAt?: number;
  completedAt?: number;
}