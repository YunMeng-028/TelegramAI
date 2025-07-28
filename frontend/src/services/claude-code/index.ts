/**
 * Claude Code SDK 主入口
 */

import { query, queryOnce, ClaudeCodeSession } from './query';
import { ToolManager, getScenarioPreset } from './tools';
import type { 
  ClaudeCodeOptions, 
  ClaudeCodeMessage, 
  ClaudeCodeResponse,
  ClaudeCodeContext,
  ClaudeCodeConfig 
} from './types';

export * from './types';
export { ClaudeCodeQueryError } from './query';

/**
 * Claude Code 服务类
 */
export class ClaudeCodeService {
  private toolManager: ToolManager;
  private config: ClaudeCodeConfig;
  private sessions: Map<string, ClaudeCodeSession> = new Map();
  
  constructor(config?: ClaudeCodeConfig) {
    this.config = {
      endpoint: process.env.CLAUDE_CODE_ENDPOINT,
      defaultOptions: {
        maxTurns: 3,
        temperature: 0.7,
        outputFormat: 'stream',
        apiKey: process.env.CLAUDE_CODE_API_KEY
      },
      retry: {
        maxAttempts: 3,
        backoffMs: 1000
      },
      logLevel: 'info',
      ...config
    };
    
    this.toolManager = new ToolManager();
  }
  
  /**
   * 执行流式查询
   */
  async* query(
    prompt: string,
    options?: ClaudeCodeOptions,
    context?: ClaudeCodeContext
  ): AsyncGenerator<ClaudeCodeMessage> {
    const mergedOptions = this.mergeOptions(options);
    
    try {
      yield* this.withRetry(async function* () {
        yield* query(prompt, mergedOptions, context);
      });
    } catch (error) {
      this.logError('Query failed', error);
      throw error;
    }
  }
  
  /**
   * 执行单次查询
   */
  async queryOnce(
    prompt: string,
    options?: ClaudeCodeOptions,
    context?: ClaudeCodeContext
  ): Promise<ClaudeCodeResponse> {
    const mergedOptions = this.mergeOptions(options);
    
    try {
      return await this.withRetryPromise(async () => {
        return await queryOnce(prompt, mergedOptions, context);
      });
    } catch (error) {
      this.logError('QueryOnce failed', error);
      throw error;
    }
  }
  
  /**
   * 创建或获取会话
   */
  getSession(sessionId?: string, options?: ClaudeCodeOptions): ClaudeCodeSession {
    const id = sessionId || this.generateSessionId();
    
    if (!this.sessions.has(id)) {
      const mergedOptions = this.mergeOptions(options);
      const session = new ClaudeCodeSession(mergedOptions, { sessionId: id });
      this.sessions.set(id, session);
    }
    
    return this.sessions.get(id)!;
  }
  
  /**
   * 使用场景预设
   */
  useScenario(scenario: 'readonly' | 'contentGeneration' | 'development'): void {
    const preset = getScenarioPreset(scenario);
    if (preset.allowedTools) {
      preset.allowedTools.forEach(tool => {
        this.toolManager.setToolPermission(tool, true);
      });
    }
  }
  
  /**
   * 获取工具管理器
   */
  getToolManager(): ToolManager {
    return this.toolManager;
  }
  
  /**
   * 合并选项
   */
  private mergeOptions(options?: ClaudeCodeOptions): ClaudeCodeOptions {
    const toolOptions = this.toolManager.buildOptions();
    return {
      ...this.config.defaultOptions,
      ...toolOptions,
      ...options
    };
  }
  
  /**
   * 带重试的异步生成器
   */
  private async* withRetry<T>(
    fn: () => AsyncGenerator<T>
  ): AsyncGenerator<T> {
    const { maxAttempts, backoffMs } = this.config.retry!;
    let lastError: Error | undefined;
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        yield* fn();
        return;
      } catch (error) {
        lastError = error as Error;
        if (attempt < maxAttempts - 1) {
          await this.delay(backoffMs * Math.pow(2, attempt));
        }
      }
    }
    
    throw lastError;
  }
  
  /**
   * 带重试的Promise
   */
  private async withRetryPromise<T>(fn: () => Promise<T>): Promise<T> {
    const { maxAttempts, backoffMs } = this.config.retry!;
    let lastError: Error | undefined;
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        if (attempt < maxAttempts - 1) {
          await this.delay(backoffMs * Math.pow(2, attempt));
        }
      }
    }
    
    throw lastError;
  }
  
  /**
   * 延迟
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  /**
   * 生成会话ID
   */
  private generateSessionId(): string {
    return `claude_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }
  
  /**
   * 记录错误
   */
  private logError(message: string, error: unknown): void {
    if (this.config.logLevel === 'error' || this.config.logLevel === 'warn') {
      console.error(`[ClaudeCode] ${message}:`, error);
    }
  }
}

/**
 * 默认服务实例
 */
export const claudeCode = new ClaudeCodeService();

/**
 * 便捷方法：执行查询
 */
export async function askClaude(
  prompt: string,
  options?: ClaudeCodeOptions
): Promise<string> {
  const response = await claudeCode.queryOnce(prompt, options);
  
  if (response.status === 'error') {
    throw new Error(response.error);
  }
  
  // 返回最后一条助手消息
  const lastMessage = response.messages
    .filter(m => m.role === 'assistant')
    .pop();
    
  return lastMessage?.content || '';
}