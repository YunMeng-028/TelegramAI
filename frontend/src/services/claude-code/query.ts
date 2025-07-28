/**
 * Claude Code 查询接口实现
 */

import type { 
  ClaudeCodeOptions, 
  ClaudeCodeMessage, 
  ClaudeCodeResponse,
  ClaudeCodeContext 
} from './types';

export class ClaudeCodeQueryError extends Error {
  constructor(message: string, public code?: string) {
    super(message);
    this.name = 'ClaudeCodeQueryError';
  }
}

/**
 * 执行Claude Code查询
 */
export async function* query(
  prompt: string,
  options?: ClaudeCodeOptions,
  context?: ClaudeCodeContext
): AsyncGenerator<ClaudeCodeMessage> {
  const { query: claudeQuery } = await import('@anthropic-ai/claude-code');
  
  try {
    // 合并选项
    const mergedOptions = {
      maxTurns: 3,
      outputFormat: 'stream' as const,
      ...options
    };
    
    // 构建查询参数
    const queryParams = {
      prompt,
      options: mergedOptions,
      ...(context && { context })
    };
    
    // 执行查询
    for await (const message of claudeQuery(queryParams)) {
      yield message;
    }
  } catch (error) {
    throw new ClaudeCodeQueryError(
      `Query failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      'QUERY_FAILED'
    );
  }
}

/**
 * 执行单次查询（非流式）
 */
export async function queryOnce(
  prompt: string,
  options?: ClaudeCodeOptions,
  context?: ClaudeCodeContext
): Promise<ClaudeCodeResponse> {
  const messages: ClaudeCodeMessage[] = [];
  const startTime = Date.now();
  
  try {
    const optionsWithFormat = {
      ...options,
      outputFormat: 'text' as const
    };
    
    for await (const message of query(prompt, optionsWithFormat, context)) {
      messages.push(message);
    }
    
    return {
      messages,
      status: 'success',
      metadata: {
        turnsUsed: messages.length,
        tokensUsed: 0, // 需要从API响应中获取
        duration: Date.now() - startTime
      }
    };
  } catch (error) {
    return {
      messages,
      status: 'error',
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * 创建持续对话会话
 */
export class ClaudeCodeSession {
  private history: ClaudeCodeMessage[] = [];
  private sessionId: string;
  
  constructor(
    private options?: ClaudeCodeOptions,
    private context?: ClaudeCodeContext
  ) {
    this.sessionId = context?.sessionId || this.generateSessionId();
  }
  
  /**
   * 发送消息到会话
   */
  async* send(prompt: string): AsyncGenerator<ClaudeCodeMessage> {
    // 添加用户消息到历史
    this.history.push({
      role: 'user',
      content: prompt,
      timestamp: Date.now()
    });
    
    // 构建带历史的上下文
    const contextWithHistory = {
      ...this.context,
      sessionId: this.sessionId,
      history: this.history
    };
    
    // 执行查询
    for await (const message of query(prompt, this.options, contextWithHistory)) {
      // 添加助手消息到历史
      if (message.role === 'assistant') {
        this.history.push({
          ...message,
          timestamp: Date.now()
        });
      }
      
      yield message;
    }
  }
  
  /**
   * 获取会话历史
   */
  getHistory(): ClaudeCodeMessage[] {
    return [...this.history];
  }
  
  /**
   * 清除会话历史
   */
  clearHistory(): void {
    this.history = [];
  }
  
  /**
   * 生成会话ID
   */
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }
}