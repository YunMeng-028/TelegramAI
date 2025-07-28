# Claude Code 集成文档

## 概述

本文档描述了 TelegramAI 项目中 Claude Code 工具组件的集成方案，包括架构设计、实现细节和使用指南。

## 集成架构

### 1. 整体架构

```
┌─────────────────────────────────────┐
│        Electron 客户端               │
│  ┌─────────────────────────────┐   │
│  │   Claude Code Vue组件        │   │
│  │   - 配置管理界面             │   │
│  │   - 权限设置                 │   │
│  │   - 测试面板                 │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │   IPC 通信桥接              │   │
│  │   - 请求/响应处理           │   │
│  │   - 流式消息支持            │   │
│  └──────────┬──────────────────┘   │
└─────────────┼───────────────────────┘
              │ ZeroMQ
┌─────────────▼───────────────────────┐
│        Python 后端服务               │
│  ┌─────────────────────────────┐   │
│  │   Claude Code SDK           │   │
│  │   - 查询接口                │   │
│  │   - 会话管理                │   │
│  │   - 工具执行                │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │   AI 生成器集成             │   │
│  │   - 智能回复生成            │   │
│  │   - 上下文管理              │   │
│  │   - 人设系统                │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 2. 核心组件

#### 2.1 前端组件

- **ClaudeCodeService**: TypeScript SDK 封装
- **ClaudeCodeIPCClient**: IPC 通信客户端
- **ClaudeCodeConfig.vue**: 配置界面组件
- **ToolManager**: 工具权限管理
- **PermissionsStore**: Pinia 状态管理

#### 2.2 后端组件

- **ClaudeCodeService**: Python SDK 封装
- **AdvancedAIGenerator**: AI 生成器集成
- **PermissionManager**: 权限管理系统
- **PerformanceMonitor**: 性能监控
- **ErrorRecovery**: 错误恢复机制

## 功能特性

### 1. 智能内容生成

集成 Claude Code 后，AI 回复生成能力得到显著提升：

- **多轮对话支持**: 支持最多 10 轮的上下文对话
- **工具增强**: 可使用 WebSearch、TodoWrite 等工具增强回复
- **动态人设**: 根据账号人设动态调整回复风格
- **智能缓存**: 相似问题的智能缓存和变化

### 2. 工具权限管理

提供细粒度的工具权限控制：

```typescript
// 工具权限配置示例
const permissions = {
  allowed_tools: ['Read', 'Grep', 'WebSearch', 'TodoWrite'],
  permissions: {
    allow: ['Bash(npm*)', 'Bash(git status)'],
    deny: ['Bash(rm*)', 'Bash(sudo*)']
  }
}
```

### 3. 场景预设

内置三种使用场景：

- **只读分析**: 安全的文件读取和搜索
- **内容生成**: 专注于内容创作和任务管理
- **完整开发**: 包含文件编辑等高级功能

### 4. 性能监控

实时监控 Claude Code 使用情况：

- 操作耗时统计
- 工具使用频率
- 错误率追踪
- 性能指标导出

## 使用指南

### 1. 配置 API 密钥

```typescript
// 在环境变量中设置
CLAUDE_CODE_API_KEY=your_api_key_here

// 或在配置界面中设置
```

### 2. 基础使用

```python
# Python 端使用示例
from telegram_ai.ai.claude_code import askClaude, ClaudeCodeOptions

# 简单查询
response = await askClaude("生成一个友好的问候语")

# 带选项的查询
options = ClaudeCodeOptions(
    temperature=0.8,
    max_turns=5,
    allowed_tools=['WebSearch', 'TodoWrite']
)
response = await askClaude("帮我搜索最新的AI发展动态", options)
```

```typescript
// TypeScript 端使用示例
import { claudeCode } from '@/services/claude-code'

// 创建会话
const session = claudeCode.getSession('chat_123')

// 发送消息
for await (const message of session.send('你好')) {
  console.log(message.content)
}
```

### 3. 集成到 AI 生成器

```python
# 在 MessageContext 中使用
context = MessageContext(
    message="用户消息",
    chat_type="group",
    account_persona=persona_data
)

# 生成增强回复
reply = await ai_generator.generate_with_tools(context)
```

### 4. 权限配置

```python
# 设置权限管理器
from telegram_ai.ai.claude_code.permissions import PermissionManager

manager = PermissionManager()

# 应用预设
manager.apply_preset("content_generation")

# 自定义权限
manager.add_allowed_tool(ClaudeCodeTool.WEB_FETCH)
manager.add_deny_rule("Bash(rm -rf*)")

# 检查权限
allowed, reason = manager.check_permission(
    ClaudeCodeTool.BASH,
    "npm install"
)
```

## 安全考虑

### 1. 工具权限

- 默认禁用危险工具（Bash、Write、Edit）
- 使用白名单机制控制命令执行
- 支持正则表达式的精确匹配

### 2. API 密钥保护

- 密钥存储在本地加密存储中
- 不在日志中记录敏感信息
- 支持环境变量配置

### 3. 错误处理

- 自动重试机制
- 降级到简单回复
- 详细的错误日志

## 性能优化

### 1. 缓存策略

- 相似查询的智能缓存
- TTL 缓存避免过期数据
- 内存限制防止溢出

### 2. 并发控制

- 限制同时进行的查询数
- 队列管理防止过载
- 自适应速率控制

### 3. 监控指标

```python
# 获取性能统计
stats = monitor.get_statistics(timedelta(hours=1))
print(f"成功率: {stats['success_rate']:.2%}")
print(f"平均耗时: {stats['average_duration']:.2f}s")

# 导出详细指标
monitor.export_metrics("claude_metrics.json")
```

## 故障排除

### 常见问题

1. **API 连接失败**
   - 检查 API 密钥是否正确
   - 确认网络连接正常
   - 查看代理设置

2. **工具执行失败**
   - 检查工具权限设置
   - 查看具体的错误信息
   - 确认命令格式正确

3. **性能问题**
   - 调整并发数限制
   - 启用缓存机制
   - 优化查询复杂度

### 日志位置

- 前端日志: `logs/renderer.log`
- 后端日志: `logs/claude_code.log`
- 性能指标: `logs/claude_metrics.json`

## 未来改进

1. **功能增强**
   - 支持更多 Claude Code 工具
   - 自定义工具开发
   - 批量操作优化

2. **性能提升**
   - 智能预加载
   - 分布式缓存
   - 流式处理优化

3. **用户体验**
   - 可视化配置界面
   - 实时预览功能
   - 一键导入导出配置

## 相关资源

- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code)
- [项目 GitHub](https://github.com/telegramai)
- [API 参考](https://docs.anthropic.com/en/docs/claude-code/sdk)