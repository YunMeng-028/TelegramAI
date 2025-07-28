<template>
  <div class="claude-code-config">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>Claude Code 配置</span>
          <el-button type="primary" size="small" @click="saveConfig">保存配置</el-button>
        </div>
      </template>
      
      <!-- API配置 -->
      <el-form :model="config" label-width="120px">
        <el-divider content-position="left">基础设置</el-divider>
        
        <el-form-item label="API密钥">
          <el-input
            v-model="config.apiKey"
            type="password"
            placeholder="请输入Claude Code API密钥"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="最大轮次">
          <el-slider
            v-model="config.maxTurns"
            :min="1"
            :max="10"
            show-input
          />
        </el-form-item>
        
        <el-form-item label="温度参数">
          <el-slider
            v-model="config.temperature"
            :min="0"
            :max="1"
            :step="0.1"
            show-input
          />
        </el-form-item>
        
        <el-form-item label="输出格式">
          <el-radio-group v-model="config.outputFormat">
            <el-radio label="text">文本</el-radio>
            <el-radio label="json">JSON</el-radio>
            <el-radio label="stream">流式</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-divider content-position="left">场景预设</el-divider>
        
        <el-form-item label="使用场景">
          <el-select v-model="selectedScenario" @change="applyScenario">
            <el-option label="自定义" value="custom" />
            <el-option label="只读分析" value="readonly" />
            <el-option label="内容生成" value="content_generation" />
            <el-option label="完整开发" value="development" />
          </el-select>
        </el-form-item>
        
        <el-divider content-position="left">工具权限</el-divider>
        
        <div class="tools-grid">
          <div
            v-for="tool in tools"
            :key="tool.name"
            class="tool-item"
          >
            <el-checkbox
              v-model="tool.allowed"
              :label="tool.displayName"
              @change="updateToolPermission(tool)"
            />
            <el-tooltip :content="tool.description" placement="top">
              <el-icon class="info-icon"><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
        </div>
        
        <el-divider content-position="left">高级权限规则</el-divider>
        
        <el-form-item label="允许规则">
          <el-tag
            v-for="(rule, index) in config.permissions.allow"
            :key="`allow-${index}`"
            closable
            @close="removeRule('allow', index)"
            class="permission-tag"
          >
            {{ rule }}
          </el-tag>
          <el-input
            v-if="showAllowInput"
            v-model="newAllowRule"
            size="small"
            style="width: 200px; margin-left: 10px"
            @keyup.enter="addRule('allow')"
            @blur="showAllowInput = false"
          />
          <el-button
            v-else
            size="small"
            @click="showAllowInput = true"
          >
            + 添加
          </el-button>
        </el-form-item>
        
        <el-form-item label="拒绝规则">
          <el-tag
            v-for="(rule, index) in config.permissions.deny"
            :key="`deny-${index}`"
            type="danger"
            closable
            @close="removeRule('deny', index)"
            class="permission-tag"
          >
            {{ rule }}
          </el-tag>
          <el-input
            v-if="showDenyInput"
            v-model="newDenyRule"
            size="small"
            style="width: 200px; margin-left: 10px"
            @keyup.enter="addRule('deny')"
            @blur="showDenyInput = false"
          />
          <el-button
            v-else
            size="small"
            @click="showDenyInput = true"
          >
            + 添加
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 测试面板 -->
    <el-card class="test-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>测试Claude Code</span>
          <el-button type="success" size="small" @click="testQuery">发送测试</el-button>
        </div>
      </template>
      
      <el-input
        v-model="testPrompt"
        type="textarea"
        :rows="3"
        placeholder="输入测试提示词..."
      />
      
      <div v-if="testResult" class="test-result">
        <el-divider content-position="left">响应结果</el-divider>
        <pre>{{ testResult }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { claudeCodeIPC } from '@/services/ipc/claude-bridge'
import type { ClaudeCodeOptions, ClaudeCodeTool } from '@/services/claude-code/types'

interface ToolConfig {
  name: ClaudeCodeTool
  displayName: string
  description: string
  allowed: boolean
}

// 配置数据
const config = reactive<ClaudeCodeOptions>({
  apiKey: '',
  maxTurns: 3,
  temperature: 0.7,
  outputFormat: 'stream',
  permissions: {
    allow: [],
    deny: []
  }
})

// 工具列表
const tools = ref<ToolConfig[]>([
  { name: 'Read', displayName: '读取文件', description: '读取文件内容', allowed: true },
  { name: 'Grep', displayName: '搜索内容', description: '搜索文件内容', allowed: true },
  { name: 'Glob', displayName: '文件匹配', description: '文件模式匹配', allowed: true },
  { name: 'TodoWrite', displayName: '任务管理', description: '创建和管理任务', allowed: true },
  { name: 'Task', displayName: '复杂任务', description: '执行复杂任务', allowed: true },
  { name: 'WebSearch', displayName: '网络搜索', description: '搜索网络信息', allowed: true },
  { name: 'WebFetch', displayName: '获取网页', description: '获取网页内容', allowed: false },
  { name: 'Bash', displayName: '系统命令', description: '执行系统命令', allowed: false },
  { name: 'Write', displayName: '写入文件', description: '写入文件内容', allowed: false },
  { name: 'Edit', displayName: '编辑文件', description: '编辑文件内容', allowed: false },
  { name: 'MultiEdit', displayName: '批量编辑', description: '批量编辑文件', allowed: false }
])

const selectedScenario = ref('custom')
const showAllowInput = ref(false)
const showDenyInput = ref(false)
const newAllowRule = ref('')
const newDenyRule = ref('')

// 测试相关
const testPrompt = ref('你好，请介绍一下自己')
const testResult = ref('')

// 加载配置
onMounted(async () => {
  try {
    const savedConfig = await window.electronAPI?.getConfig('claudeCode')
    if (savedConfig) {
      Object.assign(config, savedConfig)
      // 更新工具状态
      if (savedConfig.allowedTools) {
        tools.value.forEach(tool => {
          tool.allowed = savedConfig.allowedTools.includes(tool.name)
        })
      }
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
})

// 保存配置
const saveConfig = async () => {
  try {
    // 收集允许的工具
    config.allowedTools = tools.value
      .filter(tool => tool.allowed)
      .map(tool => tool.name)
    
    await window.electronAPI?.setConfig('claudeCode', config)
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存配置失败')
    console.error(error)
  }
}

// 应用场景预设
const applyScenario = (scenario: string) => {
  if (scenario === 'custom') return
  
  const scenarios = {
    readonly: {
      allowed: ['Read', 'Grep', 'Glob', 'LS', 'WebSearch'],
      permissions: {
        allow: [],
        deny: ['Write', 'Edit', 'Bash', 'MultiEdit']
      }
    },
    content_generation: {
      allowed: ['TodoWrite', 'Task', 'WebSearch', 'Read'],
      permissions: {
        allow: ['WebFetch'],
        deny: ['Bash', 'Write', 'Edit']
      }
    },
    development: {
      allowed: ['Read', 'Write', 'Edit', 'MultiEdit', 'Grep', 'Glob', 'LS', 'TodoWrite', 'Task', 'WebSearch', 'WebFetch'],
      permissions: {
        allow: ['Bash(npm*)', 'Bash(yarn*)', 'Bash(git*)'],
        deny: ['Bash(rm*)', 'Bash(sudo*)']
      }
    }
  }
  
  const preset = scenarios[scenario as keyof typeof scenarios]
  if (preset) {
    // 更新工具权限
    tools.value.forEach(tool => {
      tool.allowed = preset.allowed.includes(tool.name)
    })
    // 更新权限规则
    config.permissions = { ...preset.permissions }
  }
}

// 更新工具权限
const updateToolPermission = (tool: ToolConfig) => {
  // 权限更新会在保存时处理
}

// 添加权限规则
const addRule = (type: 'allow' | 'deny') => {
  const rule = type === 'allow' ? newAllowRule.value : newDenyRule.value
  if (rule && !config.permissions[type]?.includes(rule)) {
    if (!config.permissions[type]) {
      config.permissions[type] = []
    }
    config.permissions[type]!.push(rule)
    if (type === 'allow') {
      newAllowRule.value = ''
      showAllowInput.value = false
    } else {
      newDenyRule.value = ''
      showDenyInput.value = false
    }
  }
}

// 移除权限规则
const removeRule = (type: 'allow' | 'deny', index: number) => {
  config.permissions[type]?.splice(index, 1)
}

// 测试查询
const testQuery = async () => {
  if (!testPrompt.value) {
    ElMessage.warning('请输入测试提示词')
    return
  }
  
  try {
    testResult.value = '正在查询...'
    
    // 收集当前配置
    const testOptions: ClaudeCodeOptions = {
      ...config,
      allowedTools: tools.value
        .filter(tool => tool.allowed)
        .map(tool => tool.name)
    }
    
    const response = await claudeCodeIPC.queryOnce(testPrompt.value, testOptions)
    
    if (response.status === 'success') {
      const assistantMessages = response.messages.filter(m => m.role === 'assistant')
      testResult.value = assistantMessages.map(m => m.content).join('\n\n')
    } else {
      testResult.value = `错误: ${response.error}`
    }
  } catch (error) {
    testResult.value = `查询失败: ${error}`
    console.error(error)
  }
}
</script>

<style scoped>
.claude-code-config {
  padding: 20px;
}

.config-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin: 10px 0;
}

.tool-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.info-icon {
  color: #909399;
  cursor: help;
}

.permission-tag {
  margin: 0 5px 5px 0;
}

.test-card {
  max-width: 800px;
  margin: 20px auto 0;
}

.test-result {
  margin-top: 20px;
}

.test-result pre {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}
</style>