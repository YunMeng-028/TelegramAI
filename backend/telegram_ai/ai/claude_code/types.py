"""
Claude Code 类型定义
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal, TypedDict


class ClaudeCodeTool(str, Enum):
    """Claude Code 工具枚举"""

    BASH = "Bash"
    EDIT = "Edit"
    GLOB = "Glob"
    GREP = "Grep"
    LS = "LS"
    MULTI_EDIT = "MultiEdit"
    NOTEBOOK_EDIT = "NotebookEdit"
    NOTEBOOK_READ = "NotebookRead"
    READ = "Read"
    TASK = "Task"
    TODO_WRITE = "TodoWrite"
    WEB_FETCH = "WebFetch"
    WEB_SEARCH = "WebSearch"
    WRITE = "Write"


@dataclass
class ClaudeCodeOptions:
    """Claude Code 选项配置"""

    max_turns: int = 3
    system_prompt: str | None = None
    allowed_tools: list[ClaudeCodeTool] | None = None
    permissions: dict[str, list[str]] | None = None
    temperature: float = 0.7
    output_format: Literal["text", "json", "stream"] = "stream"
    api_key: str | None = None
    timeout: int | None = None


@dataclass
class ToolCall:
    """工具调用信息"""

    id: str
    tool: ClaudeCodeTool
    arguments: dict[str, Any]
    result: Any | None = None


@dataclass
class ClaudeCodeMessage:
    """Claude Code 消息"""

    role: Literal["user", "assistant", "system"]
    content: str
    tool_calls: list[ToolCall] | None = None
    timestamp: datetime | None = field(default_factory=datetime.now)


@dataclass
class ClaudeCodeResponse:
    """Claude Code 响应"""

    messages: list[ClaudeCodeMessage]
    status: Literal["success", "error", "streaming"]
    error: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class ClaudeCodeContext:
    """Claude Code 上下文"""

    session_id: str
    user: dict[str, Any] | None = None
    history: list[ClaudeCodeMessage] | None = None
    context_data: dict[str, Any] | None = None


@dataclass
class TaskResult:
    """任务执行结果"""

    task_id: str
    status: Literal["pending", "in_progress", "completed", "failed"]
    result: Any | None = None
    error: str | None = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None


@dataclass
class TodoItem:
    """待办事项"""

    id: str
    content: str
    status: Literal["pending", "in_progress", "completed"]
    priority: Literal["high", "medium", "low"]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime | None = None
    completed_at: datetime | None = None


class ToolPermission(TypedDict, total=False):
    """工具权限配置"""

    tool: ClaudeCodeTool
    allowed: bool
    restrictions: list[str] | None
    description: str | None
