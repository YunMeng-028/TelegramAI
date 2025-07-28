"""
Claude Code SDK Python实现
"""

import logging
import os
from collections import deque
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

try:
    from claude_code_sdk import ClaudeCodeOptions as SDKOptions
    from claude_code_sdk import query
except ImportError:
    # 开发时的模拟实现
    async def query(prompt: str, options: Any = None) -> AsyncGenerator[dict]:
        yield {
            "role": "assistant",
            "content": f"模拟响应: {prompt}",
            "timestamp": datetime.now().isoformat(),
        }

    SDKOptions = dict

from .context import ContextManager
from .tools import ToolManager
from .types import (
    ClaudeCodeContext,
    ClaudeCodeMessage,
    ClaudeCodeOptions,
    ClaudeCodeResponse,
)

logger = logging.getLogger(__name__)


class ClaudeCodeError(Exception):
    """Claude Code错误基类"""

    pass


class ClaudeCodeSession:
    """Claude Code会话管理"""

    def __init__(
        self,
        options: ClaudeCodeOptions | None = None,
        context: ClaudeCodeContext | None = None,
    ):
        self.options = options or ClaudeCodeOptions()
        self.context = context or ClaudeCodeContext(
            session_id=f"session_{datetime.now().timestamp()}"
        )
        self.history: deque[ClaudeCodeMessage] = deque(maxlen=100)

    async def send(self, prompt: str) -> AsyncGenerator[ClaudeCodeMessage]:
        """发送消息到会话"""
        # 添加用户消息到历史
        user_message = ClaudeCodeMessage(
            role="user", content=prompt, timestamp=datetime.now()
        )
        self.history.append(user_message)

        # 构建带历史的上下文
        context_with_history = ClaudeCodeContext(
            session_id=self.context.session_id,
            user=self.context.user,
            history=list(self.history),
            context_data=self.context.context_data,
        )

        # 执行查询
        async for message in self._query(prompt, context_with_history):
            # 添加助手消息到历史
            if message.role == "assistant":
                self.history.append(message)
            yield message

    async def _query(
        self, prompt: str, context: ClaudeCodeContext
    ) -> AsyncGenerator[ClaudeCodeMessage]:
        """执行查询"""
        # 构建SDK选项
        sdk_options = self._build_sdk_options()

        # 添加历史上下文到prompt
        if context.history:
            history_text = "\n".join(
                [
                    f"{msg.role}: {msg.content}"
                    for msg in context.history[-5:]  # 最近5条
                ]
            )
            full_prompt = f"历史对话:\n{history_text}\n\n当前问题: {prompt}"
        else:
            full_prompt = prompt

        # 调用SDK
        async for response in query(full_prompt, sdk_options):
            yield self._parse_response(response)

    def _build_sdk_options(self) -> dict[str, Any]:
        """构建SDK选项"""
        options = {
            "max_turns": self.options.max_turns,
            "temperature": self.options.temperature,
            "output_format": self.options.output_format,
        }

        if self.options.system_prompt:
            options["system_prompt"] = self.options.system_prompt

        if self.options.allowed_tools:
            options["allowed_tools"] = [
                tool.value for tool in self.options.allowed_tools
            ]

        if self.options.permissions:
            options["permissions"] = self.options.permissions

        if self.options.api_key:
            options["api_key"] = self.options.api_key

        return options

    def _parse_response(self, response: dict[str, Any]) -> ClaudeCodeMessage:
        """解析响应"""
        return ClaudeCodeMessage(
            role=response.get("role", "assistant"),
            content=response.get("content", ""),
            tool_calls=response.get("tool_calls"),
            timestamp=datetime.fromisoformat(
                response.get("timestamp", datetime.now().isoformat())
            ),
        )

    def get_history(self) -> list[ClaudeCodeMessage]:
        """获取会话历史"""
        return list(self.history)

    def clear_history(self) -> None:
        """清除会话历史"""
        self.history.clear()


class ClaudeCodeService:
    """Claude Code服务"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.tool_manager = ToolManager()
        self.context_manager = ContextManager()
        self.sessions: dict[str, ClaudeCodeSession] = {}

        # 从环境变量加载配置
        self.api_key = self.config.get("api_key") or os.getenv("CLAUDE_CODE_API_KEY")

    async def query(
        self,
        prompt: str,
        options: ClaudeCodeOptions | None = None,
        context: ClaudeCodeContext | None = None,
    ) -> AsyncGenerator[ClaudeCodeMessage]:
        """执行流式查询"""
        merged_options = self._merge_options(options)

        try:
            session = ClaudeCodeSession(merged_options, context)
            async for message in session.send(prompt):
                yield message
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise ClaudeCodeError(f"查询失败: {e!s}")

    async def query_once(
        self,
        prompt: str,
        options: ClaudeCodeOptions | None = None,
        context: ClaudeCodeContext | None = None,
    ) -> ClaudeCodeResponse:
        """执行单次查询"""
        messages: list[ClaudeCodeMessage] = []
        start_time = datetime.now()

        try:
            async for message in self.query(prompt, options, context):
                messages.append(message)

            return ClaudeCodeResponse(
                messages=messages,
                status="success",
                metadata={
                    "turns_used": len(messages),
                    "duration": (datetime.now() - start_time).total_seconds(),
                },
            )
        except Exception as e:
            return ClaudeCodeResponse(messages=messages, status="error", error=str(e))

    def get_session(
        self,
        session_id: str | None = None,
        options: ClaudeCodeOptions | None = None,
    ) -> ClaudeCodeSession:
        """获取或创建会话"""
        if not session_id:
            session_id = f"session_{datetime.now().timestamp()}"

        if session_id not in self.sessions:
            merged_options = self._merge_options(options)
            context = ClaudeCodeContext(session_id=session_id)
            self.sessions[session_id] = ClaudeCodeSession(merged_options, context)

        return self.sessions[session_id]

    def use_scenario(self, scenario: str) -> None:
        """使用场景预设"""
        self.tool_manager.apply_scenario(scenario)

    def _merge_options(self, options: ClaudeCodeOptions | None) -> ClaudeCodeOptions:
        """合并选项"""
        base_options = ClaudeCodeOptions(
            api_key=self.api_key, allowed_tools=self.tool_manager.get_allowed_tools()
        )

        if options:
            # 合并选项
            if options.max_turns is not None:
                base_options.max_turns = options.max_turns
            if options.system_prompt:
                base_options.system_prompt = options.system_prompt
            if options.temperature is not None:
                base_options.temperature = options.temperature
            if options.output_format:
                base_options.output_format = options.output_format
            if options.api_key:
                base_options.api_key = options.api_key

        return base_options


# 默认服务实例
claude_code = ClaudeCodeService()


async def askClaude(prompt: str, options: ClaudeCodeOptions | None = None) -> str:
    """便捷方法：执行查询并返回结果"""
    response = await claude_code.query_once(prompt, options)

    if response.status == "error":
        raise ClaudeCodeError(response.error or "未知错误")

    # 返回最后一条助手消息
    assistant_messages = [msg for msg in response.messages if msg.role == "assistant"]

    return assistant_messages[-1].content if assistant_messages else ""
