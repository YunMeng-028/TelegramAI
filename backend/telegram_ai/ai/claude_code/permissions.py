"""
Claude Code 权限管理系统
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from .types import ClaudeCodeTool

logger = logging.getLogger(__name__)


@dataclass
class PermissionRule:
    """权限规则"""

    pattern: str
    tool: ClaudeCodeTool | None = None
    action: str | None = None
    is_regex: bool = False

    def matches(self, tool: ClaudeCodeTool, command: str = "") -> bool:
        """检查是否匹配"""
        # 构建完整命令
        full_command = f"{tool.value}({command})" if command else tool.value

        if self.is_regex:
            return bool(re.match(self.pattern, full_command))
        # 简单通配符匹配
        pattern = self.pattern.replace("*", ".*")
        return bool(re.match(f"^{pattern}$", full_command))


@dataclass
class PermissionConfig:
    """权限配置"""

    allowed_tools: set[ClaudeCodeTool] = field(default_factory=set)
    denied_tools: set[ClaudeCodeTool] = field(default_factory=set)
    allow_rules: list[PermissionRule] = field(default_factory=list)
    deny_rules: list[PermissionRule] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "allowed_tools": [tool.value for tool in self.allowed_tools],
            "denied_tools": [tool.value for tool in self.denied_tools],
            "allow_rules": [rule.pattern for rule in self.allow_rules],
            "deny_rules": [rule.pattern for rule in self.deny_rules],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PermissionConfig":
        """从字典创建"""
        config = cls()

        if "allowed_tools" in data:
            config.allowed_tools = {
                ClaudeCodeTool(tool) for tool in data["allowed_tools"]
            }

        if "denied_tools" in data:
            config.denied_tools = {
                ClaudeCodeTool(tool) for tool in data["denied_tools"]
            }

        if "allow_rules" in data:
            config.allow_rules = [
                PermissionRule(pattern=rule) for rule in data["allow_rules"]
            ]

        if "deny_rules" in data:
            config.deny_rules = [
                PermissionRule(pattern=rule) for rule in data["deny_rules"]
            ]

        return config


class PermissionManager:
    """权限管理器"""

    def __init__(self, config: PermissionConfig | None = None):
        self.config = config or PermissionConfig()
        self._init_default_permissions()

    def _init_default_permissions(self):
        """初始化默认权限"""
        # 默认允许的安全工具
        safe_tools = {
            ClaudeCodeTool.READ,
            ClaudeCodeTool.GREP,
            ClaudeCodeTool.GLOB,
            ClaudeCodeTool.LS,
            ClaudeCodeTool.TODO_WRITE,
            ClaudeCodeTool.TASK,
            ClaudeCodeTool.WEB_SEARCH,
        }

        # 默认拒绝的危险工具
        dangerous_tools = {
            ClaudeCodeTool.BASH,
            ClaudeCodeTool.WRITE,
            ClaudeCodeTool.EDIT,
            ClaudeCodeTool.MULTI_EDIT,
        }

        self.config.allowed_tools.update(safe_tools)
        self.config.denied_tools.update(dangerous_tools)

        # 添加默认规则
        self.config.deny_rules.extend(
            [
                PermissionRule("Bash(rm*)"),
                PermissionRule("Bash(sudo*)"),
                PermissionRule("Bash(chmod 777*)"),
                PermissionRule("Bash(* | sh)"),
                PermissionRule("Bash(* | bash)"),
            ]
        )

    def check_permission(
        self, tool: ClaudeCodeTool, command: str = ""
    ) -> tuple[bool, str | None]:
        """
        检查权限

        返回: (是否允许, 拒绝原因)
        """
        # 首先检查工具是否在拒绝列表
        if tool in self.config.denied_tools:
            return False, f"工具 {tool.value} 被明确拒绝"

        # 检查拒绝规则
        for rule in self.config.deny_rules:
            if rule.matches(tool, command):
                return False, f"命令匹配拒绝规则: {rule.pattern}"

        # 检查工具是否在允许列表
        if tool not in self.config.allowed_tools:
            return False, f"工具 {tool.value} 未在允许列表中"

        # 检查允许规则（如果有特定命令）
        if command:
            # 如果有允许规则，必须匹配其中一个
            if self.config.allow_rules:
                for rule in self.config.allow_rules:
                    if rule.matches(tool, command):
                        return True, None
                return False, "命令未匹配任何允许规则"

        return True, None

    def add_allowed_tool(self, tool: ClaudeCodeTool):
        """添加允许的工具"""
        self.config.allowed_tools.add(tool)
        self.config.denied_tools.discard(tool)

    def add_denied_tool(self, tool: ClaudeCodeTool):
        """添加拒绝的工具"""
        self.config.denied_tools.add(tool)
        self.config.allowed_tools.discard(tool)

    def add_allow_rule(self, pattern: str, is_regex: bool = False):
        """添加允许规则"""
        rule = PermissionRule(pattern=pattern, is_regex=is_regex)
        if rule not in self.config.allow_rules:
            self.config.allow_rules.append(rule)

    def add_deny_rule(self, pattern: str, is_regex: bool = False):
        """添加拒绝规则"""
        rule = PermissionRule(pattern=pattern, is_regex=is_regex)
        if rule not in self.config.deny_rules:
            self.config.deny_rules.append(rule)

    def remove_allow_rule(self, pattern: str):
        """移除允许规则"""
        self.config.allow_rules = [
            r for r in self.config.allow_rules if r.pattern != pattern
        ]

    def remove_deny_rule(self, pattern: str):
        """移除拒绝规则"""
        self.config.deny_rules = [
            r for r in self.config.deny_rules if r.pattern != pattern
        ]

    def apply_preset(self, preset: str):
        """应用预设配置"""
        presets = {
            "readonly": {
                "allowed_tools": ["Read", "Grep", "Glob", "LS", "WebSearch"],
                "denied_tools": ["Write", "Edit", "Bash", "MultiEdit", "WebFetch"],
                "deny_rules": ["*"],
            },
            "content_generation": {
                "allowed_tools": ["TodoWrite", "Task", "WebSearch", "Read", "WebFetch"],
                "denied_tools": ["Bash", "Write", "Edit", "MultiEdit"],
                "deny_rules": ["Bash(*)", "Write(*)", "Edit(*)"],
            },
            "development": {
                "allowed_tools": [
                    "Read",
                    "Write",
                    "Edit",
                    "MultiEdit",
                    "Grep",
                    "Glob",
                    "LS",
                    "TodoWrite",
                    "Task",
                    "WebSearch",
                    "WebFetch",
                ],
                "denied_tools": [],
                "allow_rules": [
                    "Bash(npm*)",
                    "Bash(yarn*)",
                    "Bash(git*)",
                    "Bash(python*)",
                    "Bash(node*)",
                ],
                "deny_rules": [
                    "Bash(rm -rf*)",
                    "Bash(sudo*)",
                    "Bash(chmod 777*)",
                    "Bash(curl * | sh)",
                ],
            },
        }

        if preset not in presets:
            raise ValueError(f"未知预设: {preset}")

        preset_config = presets[preset]
        new_config = PermissionConfig.from_dict(preset_config)
        self.config = new_config

    def validate_command(self, full_command: str) -> tuple[bool, str | None]:
        """
        验证完整命令

        格式: Tool(command)
        """
        # 解析命令
        match = re.match(r"^(\w+)\((.*)\)$", full_command)
        if not match:
            return False, "无效的命令格式"

        tool_name, command = match.groups()

        try:
            tool = ClaudeCodeTool(tool_name)
        except ValueError:
            return False, f"未知工具: {tool_name}"

        return self.check_permission(tool, command)

    def get_allowed_commands(self, tool: ClaudeCodeTool) -> list[str]:
        """获取工具的允许命令示例"""
        examples = []

        for rule in self.config.allow_rules:
            if rule.pattern.startswith(f"{tool.value}("):
                # 提取命令部分
                cmd = rule.pattern[len(f"{tool.value}(") : -1]
                examples.append(cmd)

        return examples

    def export_config(self) -> str:
        """导出配置为JSON"""
        return json.dumps(self.config.to_dict(), indent=2)

    def import_config(self, config_json: str):
        """从JSON导入配置"""
        data = json.loads(config_json)
        self.config = PermissionConfig.from_dict(data)

    def get_summary(self) -> dict[str, Any]:
        """获取权限摘要"""
        return {
            "allowed_tools": len(self.config.allowed_tools),
            "denied_tools": len(self.config.denied_tools),
            "allow_rules": len(self.config.allow_rules),
            "deny_rules": len(self.config.deny_rules),
            "tools": {
                "allowed": [t.value for t in self.config.allowed_tools],
                "denied": [t.value for t in self.config.denied_tools],
            },
        }
