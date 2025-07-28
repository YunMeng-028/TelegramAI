# API 文档

## 概述

TelegramAI 提供了完整的API接口，用于管理Telegram账号、配置AI参数和监控系统状态。

## 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **认证方式**: Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

所有API请求都需要在请求头中包含有效的访问令牌：

```http
Authorization: Bearer <your_access_token>
```

### 获取访问令牌

```http
POST /auth/login
Content-Type: application/json

{
  "license_key": "your_license_key"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 账号管理

### 添加Telegram账号

```http
POST /accounts
Content-Type: application/json

{
  "phone": "+1234567890",
  "api_id": 123456,
  "api_hash": "your_api_hash",
  "proxy": {
    "type": "socks5",
    "host": "127.0.0.1",
    "port": 1080,
    "username": "user",
    "password": "pass"
  }
}
```

### 获取账号列表

```http
GET /accounts
```

**响应**:
```json
{
  "accounts": [
    {
      "id": "acc_123",
      "phone": "+1234567890",
      "username": "user123",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "status": "online",
      "created_at": "2024-01-01T00:00:00Z",
      "last_activity": "2024-01-15T12:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### 更新账号状态

```http
PUT /accounts/{account_id}/status
Content-Type: application/json

{
  "is_active": true
}
```

### 删除账号

```http
DELETE /accounts/{account_id}
```

## 监听目标管理

### 添加监听目标

```http
POST /targets
Content-Type: application/json

{
  "account_id": "acc_123",
  "target_id": "@channel_name",
  "target_type": "channel",
  "priority": 5,
  "keywords": ["AI", "技术", "编程"],
  "response_config": {
    "enabled": true,
    "delay_min": 5,
    "delay_max": 30,
    "probability": 0.8
  }
}
```

### 获取监听目标

```http
GET /targets?account_id=acc_123
```

### 更新监听目标

```http
PUT /targets/{target_id}
Content-Type: application/json

{
  "priority": 3,
  "keywords": ["AI", "机器学习"],
  "response_config": {
    "enabled": true,
    "delay_min": 10,
    "delay_max": 60,
    "probability": 0.6
  }
}
```

## AI配置管理

### 获取AI配置

```http
GET /ai/config/{account_id}
```

**响应**:
```json
{
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 150,
  "personality": {
    "traits": ["友好", "专业", "幽默"],
    "formality": 0.6,
    "enthusiasm": 0.8
  },
  "reply_templates": [
    {
      "trigger": "问候",
      "responses": ["你好！很高兴见到你", "嗨！有什么可以帮助你的吗？"]
    }
  ]
}
```

### 更新AI配置

```http
PUT /ai/config/{account_id}
Content-Type: application/json

{
  "model": "gpt-4",
  "temperature": 0.8,
  "personality": {
    "traits": ["友好", "专业"],
    "formality": 0.7,
    "enthusiasm": 0.9
  }
}
```

## 统计与监控

### 获取账号统计

```http
GET /stats/accounts/{account_id}?period=7d
```

**响应**:
```json
{
  "period": "7d",
  "messages_sent": 150,
  "messages_received": 320,
  "response_rate": 0.68,
  "average_response_time": 18.5,
  "success_rate": 0.95,
  "daily_stats": [
    {
      "date": "2024-01-15",
      "messages_sent": 25,
      "messages_received": 48,
      "response_time": 16.2
    }
  ]
}
```

### 获取系统状态

```http
GET /system/status
```

**响应**:
```json
{
  "status": "healthy",
  "uptime": 86400,
  "version": "1.0.0",
  "active_accounts": 5,
  "monitoring_targets": 15,
  "cpu_usage": 25.6,
  "memory_usage": 45.2,
  "disk_usage": 12.8,
  "last_check": "2024-01-15T12:30:00Z"
}
```

### 获取实时日志

```http
GET /logs/realtime
Accept: text/event-stream
```

**响应** (Server-Sent Events):
```
data: {"level": "info", "message": "Account acc_123 connected", "timestamp": "2024-01-15T12:30:00Z"}

data: {"level": "debug", "message": "Processing message from @channel", "timestamp": "2024-01-15T12:30:15Z"}
```

## Claude Code集成

### 执行Claude查询

```http
POST /claude/query
Content-Type: application/json

{
  "prompt": "帮我生成一个友好的回复",
  "options": {
    "temperature": 0.7,
    "max_turns": 3,
    "allowed_tools": ["WebSearch", "TodoWrite"]
  },
  "context": {
    "chat_type": "group",
    "previous_messages": ["用户刚刚分享了一个AI新闻"]
  }
}
```

**响应**:
```json
{
  "response": "哇，这个AI新闻听起来很有趣！我对人工智能的发展一直很关注。你觉得这个技术会对我们的日常生活产生什么影响呢？",
  "metadata": {
    "model": "claude-3",
    "tokens_used": 45,
    "processing_time": 1.2,
    "tools_used": ["WebSearch"]
  }
}
```

### 管理Claude工具权限

```http
PUT /claude/permissions
Content-Type: application/json

{
  "allowed_tools": ["Read", "WebSearch", "TodoWrite"],
  "denied_tools": ["Bash", "Write", "Edit"],
  "rules": {
    "allow": ["WebSearch(*)", "TodoWrite(*)"],
    "deny": ["Bash(rm*)", "Bash(sudo*)"]
  }
}
```

## 错误处理

所有API错误都遵循统一的格式：

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": {
      "field": "phone",
      "reason": "格式不正确"
    }
  },
  "timestamp": "2024-01-15T12:30:00Z",
  "request_id": "req_123456"
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| `INVALID_REQUEST` | 400 | 请求参数无效 |
| `UNAUTHORIZED` | 401 | 未授权或token无效 |
| `FORBIDDEN` | 403 | 权限不足 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `RATE_LIMITED` | 429 | 请求频率过高 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |
| `SERVICE_UNAVAILABLE` | 503 | 服务暂不可用 |

## 速率限制

API采用令牌桶算法进行速率限制：

- **普通操作**: 100请求/分钟
- **AI查询**: 20请求/分钟
- **批量操作**: 10请求/分钟

当达到速率限制时，会返回429状态码和重试信息：

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "请求频率过高，请稍后重试"
  },
  "retry_after": 60
}
```

## SDK示例

### Python SDK

```python
from telegram_ai_sdk import TelegramAIClient

# 初始化客户端
client = TelegramAIClient(
    base_url="http://localhost:8000/api/v1",
    license_key="your_license_key"
)

# 添加账号
account = client.accounts.create(
    phone="+1234567890",
    api_id=123456,
    api_hash="your_api_hash"
)

# 添加监听目标
target = client.targets.create(
    account_id=account.id,
    target_id="@channel_name",
    target_type="channel"
)

# 获取统计数据
stats = client.stats.get_account_stats(
    account_id=account.id,
    period="7d"
)
```

### JavaScript SDK

```javascript
import { TelegramAIClient } from 'telegram-ai-sdk'

// 初始化客户端
const client = new TelegramAIClient({
  baseURL: 'http://localhost:8000/api/v1',
  licenseKey: 'your_license_key'
})

// 添加账号
const account = await client.accounts.create({
  phone: '+1234567890',
  api_id: 123456,
  api_hash: 'your_api_hash'
})

// 执行Claude查询
const response = await client.claude.query({
  prompt: '生成一个友好的回复',
  options: {
    temperature: 0.7,
    max_turns: 3
  }
})
```

## Webhook支持

### 配置Webhook

```http
POST /webhooks
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "events": ["message.received", "account.status_changed"],
  "secret": "your_webhook_secret"
}
```

### Webhook事件

所有webhook事件都包含以下结构：

```json
{
  "event": "message.received",
  "timestamp": "2024-01-15T12:30:00Z",
  "data": {
    "account_id": "acc_123",
    "message": {
      "id": "msg_456",
      "text": "Hello world",
      "from": {
        "id": 123456789,
        "username": "user123"
      },
      "chat": {
        "id": -1001234567890,
        "title": "Test Group"
      }
    }
  },
  "signature": "sha256=..."
}
```

## 版本控制

API使用语义版本控制，当前版本为v1。

- **主版本号**: 不兼容的API更改
- **次版本号**: 向后兼容的功能添加
- **修订号**: 向后兼容的错误修复

## 支持

如需API支持，请联系：
- 技术支持：api-support@telegramai.com
- 文档反馈：docs@telegramai.com
- GitHub Issues：https://github.com/telegramai/TelegramAI/issues