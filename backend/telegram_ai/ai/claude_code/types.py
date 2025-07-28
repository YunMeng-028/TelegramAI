"""
Claude Code 类型定义
"""

from typing import Optional, List, Dict, Any, Literal, TypedDict
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


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
    system_prompt: Optional[str] = None
    allowed_tools: Optional[List[ClaudeCodeTool]] = None
    permissions: Optional[Dict[str, List[str]]] = None
    temperature: float = 0.7
    output_format: Literal['text', 'json', 'stream'] = 'stream'
    api_key: Optional[str] = None
    timeout: Optional[int] = None


@dataclass
class ToolCall:
    """工具调用信息"""
    id: str
    tool: ClaudeCodeTool
    arguments: Dict[str, Any]
    result: Optional[Any] = None


@dataclass
class ClaudeCodeMessage:
    """Claude Code 消息"""
    role: Literal['user', 'assistant', 'system']
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    timestamp: Optional[datetime] = field(default_factory=datetime.now)


@dataclass
class ClaudeCodeResponse:
    """Claude Code 响应"""
    messages: List[ClaudeCodeMessage]
    status: Literal['success', 'error', 'streaming']
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ClaudeCodeContext:
    """Claude Code 上下文"""
    session_id: str
    user: Optional[Dict[str, Any]] = None
    history: Optional[List[ClaudeCodeMessage]] = None
    context_data: Optional[Dict[str, Any]] = None


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    status: Literal['pending', 'in_progress', 'completed', 'failed']
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None


@dataclass
class TodoItem:
    """待办事项"""
    id: str
    content: str
    status: Literal['pending', 'in_progress', 'completed']
    priority: Literal['high', 'medium', 'low']
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class ToolPermission(TypedDict, total=False):
    """工具权限配置"""
    tool: ClaudeCodeTool
    allowed: bool
    restrictions: Optional[List[str]]
    description: Optional[str]