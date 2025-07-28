"""
AI内容生成器 - 集成Claude Code
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import random
import logging
from collections import deque

from ..config import settings
from .claude_code import (
    ClaudeCodeService,
    ClaudeCodeOptions,
    ClaudeCodeContext,
    askClaude,
    ClaudeCodeTool
)


logger = logging.getLogger(__name__)


class MessageContext:
    """消息上下文"""
    def __init__(
        self,
        message: str,
        chat_type: str,
        account_persona: Dict[str, Any],
        chat_id: str,
        user_info: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ):
        self.message = message
        self.chat_type = chat_type
        self.account_persona = account_persona
        self.chat_id = chat_id
        self.user_info = user_info
        self.conversation_history = conversation_history or []
        self.timestamp = datetime.now()


class AdvancedAIGenerator:
    """高级AI内容生成器"""
    
    def __init__(self):
        self.claude_service = ClaudeCodeService()
        self.conversation_memory = deque(maxlen=20)
        self.reply_cache = {}
        self.persona_prompts = PersonaPromptManager()
        
        # 使用内容生成场景
        self.claude_service.use_scenario("content_generation")
        
    async def generate_contextual_reply(self, context: MessageContext) -> str:
        """生成上下文相关的回复"""
        # 检查缓存
        cache_key = self._get_cache_key(context)
        if cached := self.reply_cache.get(cache_key):
            return self._vary_cached_reply(cached)
            
        # 构建Claude Code上下文
        claude_context = self._build_claude_context(context)
        
        # 构建系统提示词
        system_prompt = self.persona_prompts.build_prompt(
            persona=context.account_persona,
            chat_type=context.chat_type,
            time_context=self._get_time_context(),
            conversation_summary=await self._summarize_history()
        )
        
        # 构建Claude Code选项
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            temperature=self._calculate_temperature(context),
            max_turns=3,
            allowed_tools=[
                ClaudeCodeTool.WEB_SEARCH,
                ClaudeCodeTool.TODO_WRITE,
                ClaudeCodeTool.TASK
            ]
        )
        
        try:
            # 使用Claude Code生成回复
            reply = await askClaude(
                f"请基于以下消息生成一个自然、符合人设的回复：\n{context.message}",
                options
            )
            
            # 后处理
            reply = await self._post_process(reply, context)
            
            # 缓存
            self.reply_cache[cache_key] = reply
            
            # 添加到记忆
            self.conversation_memory.append({
                "user": context.message,
                "assistant": reply,
                "timestamp": context.timestamp
            })
            
            return reply
            
        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            # 降级到简单回复
            return await self._generate_fallback_reply(context)
            
    async def generate_with_tools(self, context: MessageContext) -> str:
        """使用工具增强的生成"""
        # 创建Claude会话
        session = self.claude_service.get_session(
            session_id=f"chat_{context.chat_id}"
        )
        
        # 构建增强的提示
        enhanced_prompt = f"""
你是一个{context.account_persona.get('description', '友好的助手')}。

当前对话场景：{context.chat_type}
用户消息：{context.message}

请根据你的人设特点生成合适的回复。如果需要，可以：
1. 使用WebSearch搜索相关信息
2. 使用TodoWrite记录重要事项
3. 使用Task处理复杂请求

回复要求：
- 自然真实，符合人设
- 适度使用表情符号（{context.account_persona.get('emoji_usage', 0.1) * 100}%概率）
- 保持适当的正式程度（{context.account_persona.get('formality', 0.5)}）
"""
        
        # 发送到会话
        messages = []
        async for message in session.send(enhanced_prompt):
            messages.append(message)
            
        # 提取最后的回复
        assistant_messages = [m for m in messages if m.role == "assistant"]
        if assistant_messages:
            return assistant_messages[-1].content
        else:
            return await self._generate_fallback_reply(context)
            
    def _build_claude_context(self, context: MessageContext) -> ClaudeCodeContext:
        """构建Claude Code上下文"""
        # 转换历史记录
        history_messages = []
        for item in context.conversation_history[-5:]:  # 最近5条
            history_messages.append({
                "role": "user",
                "content": item.get("user", ""),
                "timestamp": item.get("timestamp")
            })
            history_messages.append({
                "role": "assistant",
                "content": item.get("assistant", ""),
                "timestamp": item.get("timestamp")
            })
            
        return ClaudeCodeContext(
            session_id=f"chat_{context.chat_id}",
            user={
                "id": context.chat_id,
                "info": context.user_info
            },
            history=history_messages,
            context_data={
                "chat_type": context.chat_type,
                "persona": context.account_persona
            }
        )
        
    def _calculate_temperature(self, context: MessageContext) -> float:
        """计算温度参数"""
        base_temp = 0.7
        
        # 根据聊天类型调整
        if context.chat_type == "private":
            base_temp += 0.1
        elif context.chat_type == "group":
            base_temp -= 0.1
            
        # 根据人设调整
        enthusiasm = context.account_persona.get("enthusiasm", 0.5)
        base_temp += (enthusiasm - 0.5) * 0.2
        
        return max(0.1, min(1.0, base_temp))
        
    async def _post_process(self, reply: str, context: MessageContext) -> str:
        """后处理回复"""
        # 偶尔添加打字错误
        if random.random() < context.account_persona.get("mistake_rate", 0.02):
            reply = self._add_typo(reply)
            
        # 根据人设添加表情
        if random.random() < context.account_persona.get("emoji_usage", 0.1):
            reply = self._add_emoji(reply, context)
            
        # 长度控制
        max_length = 200 if context.chat_type == "group" else 300
        if len(reply) > max_length:
            reply = self._smart_truncate(reply, max_length)
            
        return reply
        
    def _add_typo(self, text: str) -> str:
        """添加打字错误"""
        if not text:
            return text
            
        # 随机选择一个位置
        pos = random.randint(0, len(text) - 1)
        
        # 打字错误类型
        error_types = [
            lambda s, i: s[:i] + s[i+1:],  # 删除字符
            lambda s, i: s[:i] + s[i] + s[i] + s[i+1:],  # 重复字符
            lambda s, i: s[:i] + chr(ord(s[i]) + random.choice([-1, 1])) + s[i+1:]  # 相邻键
        ]
        
        try:
            error_func = random.choice(error_types)
            return error_func(text, pos)
        except:
            return text
            
    def _add_emoji(self, text: str, context: MessageContext) -> str:
        """添加表情符号"""
        emojis = {
            "happy": ["😊", "😄", "🙂", "☺️"],
            "sad": ["😔", "😢", "😞"],
            "excited": ["🎉", "✨", "🔥", "💪"],
            "thinking": ["🤔", "💭", "🧐"],
            "love": ["❤️", "💕", "😍"],
            "funny": ["😂", "🤣", "😆"]
        }
        
        # 根据情感选择表情
        emotion = self._detect_emotion(text)
        emoji_list = emojis.get(emotion, ["👍", "✌️", "🌟"])
        
        # 随机添加到末尾
        return f"{text} {random.choice(emoji_list)}"
        
    def _detect_emotion(self, text: str) -> str:
        """简单的情感检测"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["哈哈", "好笑", "搞笑"]):
            return "funny"
        elif any(word in text_lower for word in ["开心", "高兴", "快乐"]):
            return "happy"
        elif any(word in text_lower for word in ["难过", "伤心", "糟糕"]):
            return "sad"
        elif any(word in text_lower for word in ["激动", "兴奋", "太棒"]):
            return "excited"
        elif any(word in text_lower for word in ["想", "思考", "考虑"]):
            return "thinking"
        elif any(word in text_lower for word in ["爱", "喜欢", "心"]):
            return "love"
        else:
            return "happy"
            
    def _smart_truncate(self, text: str, max_length: int) -> str:
        """智能截断文本"""
        if len(text) <= max_length:
            return text
            
        # 在句子边界截断
        sentences = text.split("。")
        result = ""
        
        for sentence in sentences:
            if len(result) + len(sentence) + 1 <= max_length:
                result += sentence + "。"
            else:
                break
                
        return result.rstrip("。") + "。" if result else text[:max_length] + "..."
        
    def _get_cache_key(self, context: MessageContext) -> str:
        """生成缓存键"""
        import hashlib
        
        key_data = f"{context.message}_{context.chat_type}_{context.account_persona.get('id', '')}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def _vary_cached_reply(self, cached: str) -> str:
        """变化缓存的回复"""
        # 小幅度修改，保持核心内容
        variations = [
            lambda s: s.replace("。", "～"),
            lambda s: s.replace("！", "!"),
            lambda s: s.replace("，", ", "),
            lambda s: f"嗯，{s}",
            lambda s: f"{s}呢",
        ]
        
        if random.random() < 0.3:
            variation = random.choice(variations)
            return variation(cached)
            
        return cached
        
    def _get_time_context(self) -> str:
        """获取时间上下文"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "早上"
        elif 12 <= hour < 14:
            return "中午"
        elif 14 <= hour < 18:
            return "下午"
        elif 18 <= hour < 22:
            return "晚上"
        else:
            return "深夜"
            
    async def _summarize_history(self) -> str:
        """总结对话历史"""
        if not self.conversation_memory:
            return "新对话"
            
        # 提取最近的主题
        recent_topics = []
        for conv in list(self.conversation_memory)[-3:]:
            # 简单的主题提取
            user_msg = conv.get("user", "")
            if len(user_msg) > 10:
                recent_topics.append(user_msg[:20] + "...")
                
        if recent_topics:
            return f"最近讨论：{', '.join(recent_topics)}"
        else:
            return "轻松聊天"
            
    async def _generate_fallback_reply(self, context: MessageContext) -> str:
        """生成降级回复"""
        fallback_replies = [
            "嗯嗯，我明白你的意思",
            "确实是这样",
            "有道理",
            "我也这么觉得",
            "说得对",
            "哈哈，是的",
            "同意你的看法"
        ]
        
        return random.choice(fallback_replies)


class PersonaPromptManager:
    """人设提示词管理器"""
    
    def build_prompt(
        self,
        persona: Dict[str, Any],
        chat_type: str,
        time_context: str,
        conversation_summary: str
    ) -> str:
        """构建人设提示词"""
        traits = persona.get("traits", ["友好", "乐于助人"])
        formality = persona.get("formality", 0.5)
        enthusiasm = persona.get("enthusiasm", 0.7)
        
        # 构建基础人设
        base_prompt = f"""
你是一个{', '.join(traits)}的人。

性格特点：
- 正式程度：{'非常随意' if formality < 0.3 else '比较随意' if formality < 0.5 else '比较正式' if formality < 0.7 else '非常正式'}
- 热情程度：{'比较冷静' if enthusiasm < 0.3 else '适度热情' if enthusiasm < 0.7 else '非常热情'}
- 当前时间：{time_context}
- 对话场景：{chat_type}聊天
- {conversation_summary}

回复原则：
1. 保持自然对话风格，不要太刻意
2. 根据时间和场景调整语气
3. 适度表达情感，但不要过度
4. 回复简洁明了，避免长篇大论
5. 偶尔使用口语化表达
"""
        
        # 根据兴趣添加专业领域
        if interests := persona.get("interests"):
            base_prompt += f"\n\n你对以下领域比较了解：{', '.join(interests)}"
            
        return base_prompt