/**
 * Claude Code IPC 通信桥接
 * 用于在Electron主进程和渲染进程之间传递Claude Code相关请求
 */

import type { 
  ClaudeCodeOptions, 
  ClaudeCodeMessage, 
  ClaudeCodeResponse,
  ClaudeCodeContext 
} from '../claude-code/types';

export interface IPCClaudeRequest {
  id: string;
  type: 'query' | 'queryOnce' | 'createSession' | 'sendToSession';
  prompt: string;
  options?: ClaudeCodeOptions;
  context?: ClaudeCodeContext;
  sessionId?: string;
  timestamp: number;
}

export interface IPCClaudeResponse {
  id: string;
  type: 'message' | 'response' | 'error' | 'complete';
  data?: ClaudeCodeMessage | ClaudeCodeResponse;
  error?: string;
  timestamp: number;
}

/**
 * Claude Code IPC 客户端（渲染进程使用）
 */
export class ClaudeCodeIPCClient {
  private listeners: Map<string, (response: IPCClaudeResponse) => void> = new Map();
  
  constructor() {
    // 监听来自主进程的响应
    if (window.electronAPI?.onClaudeResponse) {
      window.electronAPI.onClaudeResponse((response: IPCClaudeResponse) => {
        const listener = this.listeners.get(response.id);
        if (listener) {
          listener(response);
          
          // 完成或错误时移除监听器
          if (response.type === 'complete' || response.type === 'error') {
            this.listeners.delete(response.id);
          }
        }
      });
    }
  }
  
  /**
   * 执行Claude查询（流式）
   */
  async* query(
    prompt: string,
    options?: ClaudeCodeOptions,
    context?: ClaudeCodeContext
  ): AsyncGenerator<ClaudeCodeMessage> {
    const requestId = this.generateRequestId();
    const request: IPCClaudeRequest = {
      id: requestId,
      type: 'query',
      prompt,
      options,
      context,
      timestamp: Date.now()
    };
    
    // 创建响应流
    const messageQueue: ClaudeCodeMessage[] = [];
    let completed = false;
    let error: Error | null = null;
    
    // 设置监听器
    this.listeners.set(requestId, (response) => {
      if (response.type === 'message' && response.data) {
        messageQueue.push(response.data as ClaudeCodeMessage);
      } else if (response.type === 'complete') {
        completed = true;
      } else if (response.type === 'error') {
        error = new Error(response.error || 'Unknown error');
        completed = true;
      }
    });
    
    // 发送请求
    await window.electronAPI?.sendClaudeRequest(request);
    
    // 生成消息
    while (!completed || messageQueue.length > 0) {
      if (messageQueue.length > 0) {
        yield messageQueue.shift()!;
      } else {
        // 等待新消息
        await new Promise(resolve => setTimeout(resolve, 10));
      }
      
      if (error) {
        throw error;
      }
    }
  }
  
  /**
   * 执行Claude查询（单次）
   */
  async queryOnce(
    prompt: string,
    options?: ClaudeCodeOptions,
    context?: ClaudeCodeContext
  ): Promise<ClaudeCodeResponse> {
    const requestId = this.generateRequestId();
    const request: IPCClaudeRequest = {
      id: requestId,
      type: 'queryOnce',
      prompt,
      options,
      context,
      timestamp: Date.now()
    };
    
    return new Promise((resolve, reject) => {
      // 设置监听器
      this.listeners.set(requestId, (response) => {
        if (response.type === 'response' && response.data) {
          resolve(response.data as ClaudeCodeResponse);
        } else if (response.type === 'error') {
          reject(new Error(response.error || 'Unknown error'));
        }
      });
      
      // 发送请求
      window.electronAPI?.sendClaudeRequest(request);
    });
  }
  
  /**
   * 发送消息到会话
   */
  async* sendToSession(
    sessionId: string,
    prompt: string
  ): AsyncGenerator<ClaudeCodeMessage> {
    const requestId = this.generateRequestId();
    const request: IPCClaudeRequest = {
      id: requestId,
      type: 'sendToSession',
      sessionId,
      prompt,
      timestamp: Date.now()
    };
    
    // 使用与query相同的流式处理逻辑
    const messageQueue: ClaudeCodeMessage[] = [];
    let completed = false;
    let error: Error | null = null;
    
    this.listeners.set(requestId, (response) => {
      if (response.type === 'message' && response.data) {
        messageQueue.push(response.data as ClaudeCodeMessage);
      } else if (response.type === 'complete') {
        completed = true;
      } else if (response.type === 'error') {
        error = new Error(response.error || 'Unknown error');
        completed = true;
      }
    });
    
    await window.electronAPI?.sendClaudeRequest(request);
    
    while (!completed || messageQueue.length > 0) {
      if (messageQueue.length > 0) {
        yield messageQueue.shift()!;
      } else {
        await new Promise(resolve => setTimeout(resolve, 10));
      }
      
      if (error) {
        throw error;
      }
    }
  }
  
  /**
   * 生成请求ID
   */
  private generateRequestId(): string {
    return `ipc_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }
}

/**
 * 声明window.electronAPI类型
 */
declare global {
  interface Window {
    electronAPI?: {
      sendClaudeRequest: (request: IPCClaudeRequest) => Promise<void>;
      onClaudeResponse: (callback: (response: IPCClaudeResponse) => void) => void;
    };
  }
}

/**
 * 默认客户端实例
 */
export const claudeCodeIPC = new ClaudeCodeIPCClient();