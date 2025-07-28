"""
Claude Code 工具管理
"""

from typing import Any

from .types import ClaudeCodeTool, ToolPermission

# 默认工具权限配置
DEFAULT_TOOL_PERMISSIONS: list[ToolPermission] = [
    {"tool": ClaudeCodeTool.READ, "allowed": True, "description": "读取文件内容"},
    {"tool": ClaudeCodeTool.GREP, "allowed": True, "description": "搜索文件内容"},
    {"tool": ClaudeCodeTool.GLOB, "allowed": True, "description": "文件模式匹配"},
    {"tool": ClaudeCodeTool.TODO_WRITE, "allowed": True, "description": "任务管理"},
    {"tool": ClaudeCodeTool.TASK, "allowed": True, "description": "执行复杂任务"},
    {"tool": ClaudeCodeTool.WEB_SEARCH, "allowed": True, "description": "网络搜索"},
    {
        "tool": ClaudeCodeTool.WEB_FETCH,
        "allowed": False,
        "description": "获取网页内容（需要额外权限）",
    },
    {
        "tool": ClaudeCodeTool.BASH,
        "allowed": False,
        "description": "执行系统命令（需要额外权限）",
    },
    {
        "tool": ClaudeCodeTool.WRITE,
        "allowed": False,
        "description": "写入文件（需要额外权限）",
    },
    {
        "tool": ClaudeCodeTool.EDIT,
        "allowed": False,
        "description": "编辑文件（需要额外权限）",
    },
]


# 场景预设配置
SCENARIO_PRESETS = {
    "readonly": {
        "name": "只读分析",
        "allowed_tools": [
            ClaudeCodeTool.READ,
            ClaudeCodeTool.GREP,
            ClaudeCodeTool.GLOB,
            ClaudeCodeTool.LS,
            ClaudeCodeTool.WEB_SEARCH,
        ],
        "permissions": {"deny": ["Write", "Edit", "Bash", "MultiEdit"]},
    },
    "content_generation": {
        "name": "内容生成",
        "allowed_tools": [
            ClaudeCodeTool.TODO_WRITE,
            ClaudeCodeTool.TASK,
            ClaudeCodeTool.WEB_SEARCH,
            ClaudeCodeTool.READ,
        ],
        "permissions": {"allow": ["WebFetch"], "deny": ["Bash", "Write", "Edit"]},
    },
    "development": {
        "name": "完整开发",
        "allowed_tools": [
            ClaudeCodeTool.READ,
            ClaudeCodeTool.WRITE,
            ClaudeCodeTool.EDIT,
            ClaudeCodeTool.MULTI_EDIT,
            ClaudeCodeTool.GREP,
            ClaudeCodeTool.GLOB,
            ClaudeCodeTool.LS,
            ClaudeCodeTool.TODO_WRITE,
            ClaudeCodeTool.TASK,
            ClaudeCodeTool.WEB_SEARCH,
            ClaudeCodeTool.WEB_FETCH,
        ],
        "permissions": {
            "allow": ["Bash(npm*)", "Bash(yarn*)", "Bash(git*)"],
            "deny": ["Bash(rm*)", "Bash(sudo*)"],
        },
    },
}


class ToolManager:
    """工具管理器"""

    def __init__(self, custom_permissions: list[ToolPermission] | None = None):
        self.permissions: dict[ClaudeCodeTool, ToolPermission] = {}

        # 加载默认权限
        for perm in DEFAULT_TOOL_PERMISSIONS:
            self.permissions[perm["tool"]] = perm

        # 覆盖自定义权限
        if custom_permissions:
            for perm in custom_permissions:
                self.permissions[perm["tool"]] = perm

    def get_allowed_tools(self) -> list[ClaudeCodeTool]:
        """获取允许的工具列表"""
        return [
            tool
            for tool, perm in self.permissions.items()
            if perm.get("allowed", False)
        ]

    def is_tool_allowed(self, tool: ClaudeCodeTool) -> bool:
        """检查工具是否允许"""
        perm = self.permissions.get(tool)
        return perm.get("allowed", False) if perm else False

    def set_tool_permission(
        self,
        tool: ClaudeCodeTool,
        allowed: bool,
        restrictions: list[str] | None = None,
    ) -> None:
        """设置工具权限"""
        if tool not in self.permissions:
            self.permissions[tool] = {"tool": tool}

        self.permissions[tool]["allowed"] = allowed
        if restrictions:
            self.permissions[tool]["restrictions"] = restrictions

    def apply_scenario(self, scenario: str) -> None:
        """应用场景预设"""
        if scenario not in SCENARIO_PRESETS:
            raise ValueError(f"未知场景: {scenario}")

        preset = SCENARIO_PRESETS[scenario]

        # 先禁用所有工具
        for tool in ClaudeCodeTool:
            self.set_tool_permission(tool, False)

        # 启用场景中的工具
        for tool in preset["allowed_tools"]:
            self.set_tool_permission(tool, True)

    def build_permissions(self) -> dict[str, list[str]]:
        """构建权限配置"""
        permissions = {"allow": [], "deny": []}

        for tool, perm in self.permissions.items():
            if perm.get("allowed"):
                if restrictions := perm.get("restrictions"):
                    # 有限制的允许
                    for restriction in restrictions:
                        permissions["allow"].append(f"{tool.value}({restriction})")
                else:
                    # 完全允许
                    permissions["allow"].append(tool.value)
            else:
                # 拒绝
                permissions["deny"].append(tool.value)

        return permissions

    def export_permissions(self) -> list[ToolPermission]:
        """导出权限配置"""
        return list(self.permissions.values())

    def import_permissions(self, permissions: list[ToolPermission]) -> None:
        """导入权限配置"""
        for perm in permissions:
            self.permissions[perm["tool"]] = perm

    def get_tool_description(self, tool: ClaudeCodeTool) -> str | None:
        """获取工具描述"""
        perm = self.permissions.get(tool)
        return perm.get("description") if perm else None

    def get_scenario_info(self, scenario: str) -> dict[str, Any] | None:
        """获取场景信息"""
        if scenario not in SCENARIO_PRESETS:
            return None

        preset = SCENARIO_PRESETS[scenario]
        return {
            "name": preset["name"],
            "allowed_tools": [tool.value for tool in preset["allowed_tools"]],
            "tool_count": len(preset["allowed_tools"]),
        }
