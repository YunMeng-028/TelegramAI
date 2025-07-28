/**
 * Electron 预加载脚本
 */

const { contextBridge, ipcRenderer } = require('electron');

// 暴露Claude Code API到渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // Claude Code相关
  sendClaudeRequest: (request) => ipcRenderer.invoke('claude-request', request),
  onClaudeResponse: (callback) => ipcRenderer.on('claude-response', (event, response) => callback(response)),
  
  // 通用IPC通信
  send: (channel, data) => {
    const validChannels = ['toMain'];
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, data);
    }
  },
  
  receive: (channel, func) => {
    const validChannels = ['fromMain'];
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (event, ...args) => func(...args));
    }
  },
  
  // 文件系统操作
  readFile: (path) => ipcRenderer.invoke('read-file', path),
  writeFile: (path, content) => ipcRenderer.invoke('write-file', path, content),
  
  // 配置管理
  getConfig: (key) => ipcRenderer.invoke('get-config', key),
  setConfig: (key, value) => ipcRenderer.invoke('set-config', key, value),
  
  // 系统信息
  getSystemInfo: () => ipcRenderer.invoke('get-system-info'),
  
  // 授权管理
  validateLicense: (key) => ipcRenderer.invoke('validate-license', key),
  getLicenseStatus: () => ipcRenderer.invoke('get-license-status')
});