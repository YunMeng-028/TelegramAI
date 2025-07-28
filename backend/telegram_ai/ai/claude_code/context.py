"""
Claude Code 上下文管理
"""

import json
from datetime import datetime
from typing import Any

from .types import ClaudeCodeContext, ClaudeCodeMessage


class ContextManager:
    """上下文管理器"""

    def __init__(self):
        self.contexts: dict[str, ClaudeCodeContext] = {}

    def create_context(
        self,
        session_id: str | None = None,
        user: dict[str, Any] | None = None,
        context_data: dict[str, Any] | None = None,
    ) -> ClaudeCodeContext:
        """创建新上下文"""
        if not session_id:
            session_id = f"ctx_{datetime.now().timestamp()}"

        context = ClaudeCodeContext(
            session_id=session_id,
            user=user,
            history=[],
            context_data=context_data or {},
        )

        self.contexts[session_id] = context
        return context

    def get_context(self, session_id: str) -> ClaudeCodeContext | None:
        """获取上下文"""
        return self.contexts.get(session_id)

    def update_context(
        self,
        session_id: str,
        user: dict[str, Any] | None = None,
        context_data: dict[str, Any] | None = None,
        history: list[ClaudeCodeMessage] | None = None,
    ) -> None:
        """更新上下文"""
        context = self.contexts.get(session_id)
        if not context:
            return

        if user is not None:
            context.user = user
        if context_data is not None:
            context.context_data.update(context_data)
        if history is not None:
            context.history = history

    def add_message(self, session_id: str, message: ClaudeCodeMessage) -> None:
        """添加消息到历史"""
        context = self.contexts.get(session_id)
        if context:
            if context.history is None:
                context.history = []
            context.history.append(message)

    def clear_history(self, session_id: str) -> None:
        """清除历史"""
        context = self.contexts.get(session_id)
        if context:
            context.history = []

    def delete_context(self, session_id: str) -> None:
        """删除上下文"""
        if session_id in self.contexts:
            del self.contexts[session_id]

    def export_context(self, session_id: str) -> dict[str, Any] | None:
        """导出上下文为字典"""
        context = self.contexts.get(session_id)
        if not context:
            return None

        return {
            "session_id": context.session_id,
            "user": context.user,
            "history": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                }
                for msg in (context.history or [])
            ],
            "context_data": context.context_data,
        }

    def import_context(self, data: dict[str, Any]) -> ClaudeCodeContext:
        """从字典导入上下文"""
        history = []
        for msg_data in data.get("history", []):
            timestamp = None
            if msg_data.get("timestamp"):
                timestamp = datetime.fromisoformat(msg_data["timestamp"])

            history.append(
                ClaudeCodeMessage(
                    role=msg_data["role"],
                    content=msg_data["content"],
                    timestamp=timestamp,
                )
            )

        context = ClaudeCodeContext(
            session_id=data["session_id"],
            user=data.get("user"),
            history=history,
            context_data=data.get("context_data", {}),
        )

        self.contexts[context.session_id] = context
        return context

    def save_to_file(self, session_id: str, filepath: str) -> None:
        """保存上下文到文件"""
        data = self.export_context(session_id)
        if data:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath: str) -> ClaudeCodeContext | None:
        """从文件加载上下文"""
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            return self.import_context(data)
        except Exception:
            return None

    def get_context_summary(self, session_id: str) -> dict[str, Any] | None:
        """获取上下文摘要"""
        context = self.contexts.get(session_id)
        if not context:
            return None

        history_length = len(context.history) if context.history else 0
        last_message = None
        if context.history and history_length > 0:
            last_msg = context.history[-1]
            last_message = {
                "role": last_msg.role,
                "content": (
                    last_msg.content[:100] + "..."
                    if len(last_msg.content) > 100
                    else last_msg.content
                ),
                "timestamp": (
                    last_msg.timestamp.isoformat() if last_msg.timestamp else None
                ),
            }

        return {
            "session_id": context.session_id,
            "user_id": context.user.get("id") if context.user else None,
            "history_length": history_length,
            "last_message": last_message,
            "context_keys": (
                list(context.context_data.keys()) if context.context_data else []
            ),
        }
