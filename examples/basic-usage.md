# TelegramAI 基础使用示例

本文档展示了 TelegramAI 的基本使用方法和常见场景。

## 目录

- [快速开始](#快速开始)
- [账户管理](#账户管理)
- [消息处理](#消息处理)
- [群组管理](#群组管理)
- [AI 内容生成](#ai-内容生成)
- [自动化任务](#自动化任务)

## 快速开始

### 1. 启动应用

```bash
# 开发模式
npm run electron:dev

# 生产模式
./TelegramAI
```

### 2. 添加第一个账户

```typescript
// 在应用中添加账户
const account = {
  phone: '+1234567890',
  name: '我的账户',
  apiId: 'your_api_id',
  apiHash: 'your_api_hash'
}

await accountService.addAccount(account)
```

### 3. 配置 AI 服务

```typescript
// 配置 Claude AI
const aiConfig = {
  provider: 'claude',
  apiKey: 'your_claude_api_key',
  model: 'claude-3-sonnet-20240229'
}

await aiService.configure(aiConfig)
```

## 账户管理

### 添加账户

```typescript
import { AccountService } from '@/services/account'

const accountService = new AccountService()

// 添加新账户
const newAccount = await accountService.addAccount({
  phone: '+1234567890',
  name: '主账户',
  apiId: 'your_api_id',
  apiHash: 'your_api_hash',
  proxy: {
    type: 'socks5',
    host: '127.0.0.1',
    port: 1080
  }
})

console.log('账户添加成功:', newAccount.id)
```

### 获取账户列表

```typescript
// 获取所有账户
const accounts = await accountService.getAccounts()

// 获取在线账户
const onlineAccounts = accounts.filter(account => account.status === 'online')

console.log(`共有 ${accounts.length} 个账户，${onlineAccounts.length} 个在线`)
```

### 账户状态管理

```typescript
// 连接账户
await accountService.connect(accountId)

// 断开连接
await accountService.disconnect(accountId)

// 检查账户状态
const status = await accountService.getStatus(accountId)
console.log('账户状态:', status)
```

## 消息处理

### 发送消息

```typescript
import { MessageService } from '@/services/message'

const messageService = new MessageService()

// 发送文本消息
await messageService.sendText({
  accountId: 'account-1',
  chatId: 'user123',
  text: '你好！这是一条测试消息。'
})

// 发送图片
await messageService.sendPhoto({
  accountId: 'account-1',
  chatId: 'user123',
  photo: './images/example.jpg',
  caption: '这是图片说明'
})

// 发送文件
await messageService.sendDocument({
  accountId: 'account-1',
  chatId: 'user123',
  document: './files/document.pdf',
  filename: '重要文档.pdf'
})
```

### 接收消息处理

```typescript
// 监听新消息
messageService.on('newMessage', async (message) => {
  console.log('收到新消息:', message)
  
  // 自动回复
  if (message.text?.includes('你好')) {
    await messageService.sendText({
      accountId: message.accountId,
      chatId: message.chat.id,
      text: '你好！很高兴见到你！'
    })
  }
})

// 处理特定类型消息
messageService.on('newMessage', async (message) => {
  if (message.media?.photo) {
    console.log('收到图片消息')
    // 处理图片
  }
  
  if (message.media?.document) {
    console.log('收到文件消息')
    // 处理文件
  }
})
```

## 群组管理

### 加入群组

```typescript
import { GroupService } from '@/services/group'

const groupService = new GroupService()

// 通过邀请链接加入
await groupService.joinByLink({
  accountId: 'account-1',
  inviteLink: 'https://t.me/joinchat/xxx'
})

// 通过用户名加入
await groupService.joinByUsername({
  accountId: 'account-1',
  username: 'example_group'
})
```

### 获取群组成员

```typescript
// 获取群组成员列表
const members = await groupService.getMembers({
  accountId: 'account-1',
  chatId: 'group123'
})

console.log(`群组有 ${members.length} 个成员`)

// 获取管理员
const admins = members.filter(member => member.isAdmin)
console.log(`其中 ${admins.length} 个管理员`)
```

### 群组消息管理

```typescript
// 发送群组公告
await messageService.sendText({
  accountId: 'account-1',
  chatId: 'group123',
  text: '📢 重要通知：明天将进行系统维护',
  pinMessage: true
})

// 删除消息
await messageService.deleteMessage({
  accountId: 'account-1',
  chatId: 'group123',
  messageId: 'msg123'
})
```

## AI 内容生成

### 配置 AI 服务

```typescript
import { AIService } from '@/services/ai'

const aiService = new AIService()

// 配置 Claude
await aiService.configure({
  provider: 'claude',
  apiKey: 'your_api_key',
  model: 'claude-3-sonnet-20240229',
  maxTokens: 1000,
  temperature: 0.7
})
```

### 生成回复内容

```typescript
// 基于消息历史生成回复
const reply = await aiService.generateReply({
  context: {
    chat: 'group123',
    messages: [
      { text: '今天天气怎么样？', sender: 'user1' },
      { text: '很晴朗，适合出门', sender: 'user2' }
    ]
  },
  prompt: '友好、自然地参与对话'
})

console.log('AI 生成的回复:', reply.text)
```

### 内容总结

```typescript
// 总结聊天记录
const summary = await aiService.summarize({
  content: [
    '用户1: 我们讨论一下项目进度',
    '用户2: 目前完成了 60%',
    '用户3: 预计下周可以完成'
  ],
  type: 'chat_summary'
})

console.log('聊天总结:', summary.text)
```

### 智能分类

```typescript
// 消息分类
const classification = await aiService.classify({
  text: '这个产品有什么优惠吗？',
  categories: ['询价', '投诉', '建议', '其他']
})

console.log('消息分类:', classification.category)
```

## 自动化任务

### 创建定时任务

```typescript
import { SchedulerService } from '@/services/scheduler'

const scheduler = new SchedulerService()

// 每天早上发送问候
scheduler.createTask({
  name: '早安问候',
  schedule: '0 9 * * *', // 每天 9:00
  action: async () => {
    await messageService.sendText({
      accountId: 'account-1',
      chatId: 'group123',
      text: '🌅 早上好！新的一天开始了！'
    })
  }
})

// 每小时备份重要消息
scheduler.createTask({
  name: '消息备份',
  schedule: '0 * * * *', // 每小时
  action: async () => {
    await backupService.backupMessages('important_group')
  }
})
```

### 自动回复规则

```typescript
import { AutoReplyService } from '@/services/auto-reply'

const autoReply = new AutoReplyService()

// 添加关键词回复
autoReply.addRule({
  name: '问候回复',
  trigger: {
    type: 'keyword',
    keywords: ['你好', 'hello', 'hi']
  },
  response: {
    type: 'text',
    content: '你好！有什么可以帮助你的吗？'
  },
  conditions: {
    chatTypes: ['private'], // 仅在私聊中生效
    timeRange: { start: '09:00', end: '18:00' } // 工作时间
  }
})

// 添加 AI 驱动的智能回复
autoReply.addRule({
  name: '智能客服',
  trigger: {
    type: 'ai_classification',
    categories: ['问题', '咨询']
  },
  response: {
    type: 'ai_generated',
    prompt: '作为客服代表，专业、友好地回答用户问题'
  }
})
```

### 批量操作

```typescript
// 批量发送消息
const targets = ['user1', 'user2', 'user3']
const message = '🎉 产品更新通知：新版本已发布！'

for (const target of targets) {
  await messageService.sendText({
    accountId: 'account-1',
    chatId: target,
    text: message
  })
  
  // 避免频率限制
  await new Promise(resolve => setTimeout(resolve, 1000))
}

// 批量邀请用户到群组
const users = await contactService.getContacts(accountId)
const activeUsers = users.filter(user => user.lastSeen > Date.now() - 7 * 24 * 60 * 60 * 1000)

for (const user of activeUsers) {
  try {
    await groupService.inviteUser({
      accountId: 'account-1',
      chatId: 'group123',
      userId: user.id
    })
    console.log(`成功邀请用户: ${user.name}`)
  } catch (error) {
    console.log(`邀请失败: ${user.name} - ${error.message}`)
  }
}
```

## 错误处理

### 通用错误处理

```typescript
try {
  await messageService.sendText({
    accountId: 'account-1',
    chatId: 'user123',
    text: '测试消息'
  })
} catch (error) {
  if (error.code === 'USER_BLOCKED') {
    console.log('用户已屏蔽')
  } else if (error.code === 'FLOOD_WAIT') {
    console.log(`需要等待 ${error.seconds} 秒`)
    await new Promise(resolve => setTimeout(resolve, error.seconds * 1000))
  } else {
    console.error('发送失败:', error.message)
  }
}
```

### 重试机制

```typescript
async function sendWithRetry(params, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await messageService.sendText(params)
    } catch (error) {
      if (i === maxRetries - 1) throw error
      
      console.log(`第 ${i + 1} 次尝试失败，等待重试...`)
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)))
    }
  }
}
```

## 最佳实践

### 1. 频率控制

```typescript
// 使用队列控制发送频率
class MessageQueue {
  private queue = []
  private processing = false
  private interval = 1000 // 1秒间隔
  
  async add(messageParams) {
    this.queue.push(messageParams)
    if (!this.processing) {
      this.process()
    }
  }
  
  private async process() {
    this.processing = true
    
    while (this.queue.length > 0) {
      const params = this.queue.shift()
      try {
        await messageService.sendText(params)
      } catch (error) {
        console.error('发送失败:', error)
      }
      
      await new Promise(resolve => setTimeout(resolve, this.interval))
    }
    
    this.processing = false
  }
}
```

### 2. 数据持久化

```typescript
// 保存重要数据
await dataService.save('contacts', contacts)
await dataService.save('messages', recentMessages)
await dataService.save('settings', userSettings)

// 定期备份
setInterval(async () => {
  await backupService.createBackup()
}, 60 * 60 * 1000) // 每小时备份
```

### 3. 监控和日志

```typescript
// 记录操作日志
logger.info('发送消息', { accountId, chatId, messageLength: text.length })
logger.error('操作失败', { error: error.message, stack: error.stack })

// 监控系统状态
setInterval(async () => {
  const stats = await systemService.getStats()
  logger.info('系统状态', stats)
}, 5 * 60 * 1000) // 每5分钟记录状态
```

## 故障排除

### 常见问题

1. **连接失败**
   - 检查网络连接
   - 验证 API 凭据
   - 确认代理设置

2. **消息发送失败**
   - 检查账户状态
   - 验证目标用户/群组
   - 检查频率限制

3. **AI 服务异常**
   - 验证 API 密钥
   - 检查配额限制
   - 确认网络连接

### 调试模式

```typescript
// 启用详细日志
process.env.DEBUG = 'telegram-ai:*'

// 或在代码中设置
logger.setLevel('debug')
```

更多详细示例请参考 `examples/` 目录中的其他文件。
