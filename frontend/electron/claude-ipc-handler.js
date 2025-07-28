/**
 * Claude Code IPC 处理器（主进程）
 */

const { ipcMain } = require('electron');
const { ClaudeCodeService } = require('../src/services/claude-code');

class ClaudeIPCHandler {
  constructor() {
    this.claudeService = new ClaudeCodeService();
    this.sessions = new Map();
    this.setupHandlers();
  }

  setupHandlers() {
    // 处理Claude请求
    ipcMain.handle('claude-request', async (event, request) => {
      try {
        switch (request.type) {
          case 'query':
            return await this.handleQuery(event, request);
          case 'queryOnce':
            return await this.handleQueryOnce(request);
          case 'createSession':
            return await this.handleCreateSession(request);
          case 'sendToSession':
            return await this.handleSendToSession(event, request);
          default:
            throw new Error(`Unknown request type: ${request.type}`);
        }
      } catch (error) {
        return {
          id: request.id,
          type: 'error',
          error: error.message,
          timestamp: Date.now()
        };
      }
    });
  }

  /**
   * 处理流式查询
   */
  async handleQuery(event, request) {
    const { id, prompt, options, context } = request;
    
    try {
      // 开始流式查询
      for await (const message of this.claudeService.query(prompt, options, context)) {
        // 发送消息到渲染进程
        event.sender.send('claude-response', {
          id,
          type: 'message',
          data: message,
          timestamp: Date.now()
        });
      }
      
      // 发送完成信号
      event.sender.send('claude-response', {
        id,
        type: 'complete',
        timestamp: Date.now()
      });
    } catch (error) {
      // 发送错误
      event.sender.send('claude-response', {
        id,
        type: 'error',
        error: error.message,
        timestamp: Date.now()
      });
    }
    
    return { success: true };
  }

  /**
   * 处理单次查询
   */
  async handleQueryOnce(request) {
    const { id, prompt, options, context } = request;
    
    try {
      const response = await this.claudeService.queryOnce(prompt, options, context);
      
      return {
        id,
        type: 'response',
        data: response,
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        id,
        type: 'error',
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  /**
   * 处理创建会话
   */
  async handleCreateSession(request) {
    const { id, sessionId, options } = request;
    
    try {
      const session = this.claudeService.getSession(sessionId, options);
      this.sessions.set(sessionId || session.sessionId, session);
      
      return {
        id,
        type: 'response',
        data: { sessionId: session.sessionId },
        timestamp: Date.now()
      };
    } catch (error) {
      return {
        id,
        type: 'error',
        error: error.message,
        timestamp: Date.now()
      };
    }
  }

  /**
   * 处理发送到会话
   */
  async handleSendToSession(event, request) {
    const { id, sessionId, prompt } = request;
    
    try {
      const session = this.sessions.get(sessionId);
      if (!session) {
        throw new Error(`Session not found: ${sessionId}`);
      }
      
      // 发送消息到会话
      for await (const message of session.send(prompt)) {
        event.sender.send('claude-response', {
          id,
          type: 'message',
          data: message,
          timestamp: Date.now()
        });
      }
      
      // 发送完成信号
      event.sender.send('claude-response', {
        id,
        type: 'complete',
        timestamp: Date.now()
      });
    } catch (error) {
      event.sender.send('claude-response', {
        id,
        type: 'error',
        error: error.message,
        timestamp: Date.now()
      });
    }
    
    return { success: true };
  }

  /**
   * 清理资源
   */
  cleanup() {
    this.sessions.clear();
  }
}

// 导出处理器
module.exports = { ClaudeIPCHandler };