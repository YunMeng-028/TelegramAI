"""
Claude Code 性能监控和错误处理
"""

import time
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
import logging
import json

from .types import ClaudeCodeTool


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """性能指标"""
    operation: str
    duration: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolUsageStats:
    """工具使用统计"""
    tool: ClaudeCodeTool
    count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_duration: float = 0.0
    last_used: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_history: int = 1000):
        self.metrics: deque[PerformanceMetric] = deque(maxlen=max_history)
        self.tool_stats: Dict[ClaudeCodeTool, ToolUsageStats] = {}
        self.error_handlers: List[Callable] = []
        self._start_times: Dict[str, float] = {}
        
    async def track_operation(self, operation: str, metadata: Dict[str, Any] = None):
        """跟踪操作性能（上下文管理器）"""
        operation_id = f"{operation}_{time.time()}"
        self._start_times[operation_id] = time.perf_counter()
        
        class OperationContext:
            def __init__(self, monitor, op_id, op_name, meta):
                self.monitor = monitor
                self.op_id = op_id
                self.op_name = op_name
                self.meta = meta or {}
                self.error = None
                
            async def __aenter__(self):
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                duration = time.perf_counter() - self.monitor._start_times.pop(self.op_id)
                success = exc_type is None
                error_msg = str(exc_val) if exc_val else None
                
                # 记录指标
                metric = PerformanceMetric(
                    operation=self.op_name,
                    duration=duration,
                    timestamp=datetime.now(),
                    success=success,
                    error=error_msg,
                    metadata=self.meta
                )
                
                self.monitor.metrics.append(metric)
                
                # 更新工具统计（如果是工具操作）
                if tool_name := self.meta.get("tool"):
                    try:
                        tool = ClaudeCodeTool(tool_name)
                        self.monitor._update_tool_stats(tool, duration, success, error_msg)
                    except ValueError:
                        pass
                
                # 错误处理
                if not success and error_msg:
                    await self.monitor._handle_error(self.op_name, error_msg, self.meta)
                    
                # 性能警告
                if duration > self.monitor._get_threshold(self.op_name):
                    logger.warning(
                        f"操作 {self.op_name} 执行时间过长: {duration:.2f}s"
                    )
                    
                return False  # 不抑制异常
                
        return OperationContext(self, operation_id, operation, metadata)
        
    def _update_tool_stats(
        self,
        tool: ClaudeCodeTool,
        duration: float,
        success: bool,
        error: Optional[str]
    ):
        """更新工具使用统计"""
        if tool not in self.tool_stats:
            self.tool_stats[tool] = ToolUsageStats(tool=tool)
            
        stats = self.tool_stats[tool]
        stats.count += 1
        stats.total_duration += duration
        stats.last_used = datetime.now()
        
        if success:
            stats.success_count += 1
        else:
            stats.error_count += 1
            if error and error not in stats.errors:
                stats.errors.append(error)
                if len(stats.errors) > 10:  # 保留最近10个错误
                    stats.errors.pop(0)
                    
    async def _handle_error(self, operation: str, error: str, metadata: Dict[str, Any]):
        """处理错误"""
        for handler in self.error_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(operation, error, metadata)
                else:
                    handler(operation, error, metadata)
            except Exception as e:
                logger.error(f"错误处理器失败: {e}")
                
    def _get_threshold(self, operation: str) -> float:
        """获取操作的性能阈值"""
        thresholds = {
            "query": 5.0,
            "query_once": 5.0,
            "tool_execution": 3.0,
            "web_search": 10.0,
            "web_fetch": 8.0,
            "task": 15.0
        }
        
        return thresholds.get(operation, 5.0)
        
    def add_error_handler(self, handler: Callable):
        """添加错误处理器"""
        self.error_handlers.append(handler)
        
    def get_statistics(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """获取统计信息"""
        if time_window:
            cutoff = datetime.now() - time_window
            relevant_metrics = [
                m for m in self.metrics
                if m.timestamp > cutoff
            ]
        else:
            relevant_metrics = list(self.metrics)
            
        if not relevant_metrics:
            return {
                "total_operations": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "operations_by_type": {},
                "errors": []
            }
            
        # 计算统计
        total = len(relevant_metrics)
        successful = sum(1 for m in relevant_metrics if m.success)
        total_duration = sum(m.duration for m in relevant_metrics)
        
        # 按操作类型分组
        by_operation = defaultdict(list)
        for metric in relevant_metrics:
            by_operation[metric.operation].append(metric)
            
        operations_stats = {}
        for op, metrics in by_operation.items():
            op_total = len(metrics)
            op_successful = sum(1 for m in metrics if m.success)
            op_duration = sum(m.duration for m in metrics)
            
            operations_stats[op] = {
                "count": op_total,
                "success_rate": op_successful / op_total if op_total > 0 else 0,
                "average_duration": op_duration / op_total if op_total > 0 else 0,
                "errors": [m.error for m in metrics if m.error][:5]  # 最近5个错误
            }
            
        # 收集所有错误
        all_errors = [
            {"operation": m.operation, "error": m.error, "timestamp": m.timestamp.isoformat()}
            for m in relevant_metrics
            if m.error
        ][:10]  # 最近10个错误
        
        return {
            "total_operations": total,
            "success_rate": successful / total if total > 0 else 0,
            "average_duration": total_duration / total if total > 0 else 0,
            "operations_by_type": operations_stats,
            "errors": all_errors,
            "time_window": str(time_window) if time_window else "all"
        }
        
    def get_tool_statistics(self) -> Dict[str, Any]:
        """获取工具使用统计"""
        tool_data = {}
        
        for tool, stats in self.tool_stats.items():
            if stats.count == 0:
                continue
                
            tool_data[tool.value] = {
                "count": stats.count,
                "success_count": stats.success_count,
                "error_count": stats.error_count,
                "success_rate": stats.success_count / stats.count if stats.count > 0 else 0,
                "average_duration": stats.total_duration / stats.count if stats.count > 0 else 0,
                "last_used": stats.last_used.isoformat() if stats.last_used else None,
                "recent_errors": stats.errors[-3:]  # 最近3个错误
            }
            
        return {
            "tools": tool_data,
            "most_used": max(tool_data.items(), key=lambda x: x[1]["count"])[0] if tool_data else None,
            "most_errors": max(tool_data.items(), key=lambda x: x[1]["error_count"])[0] if tool_data else None
        }
        
    def export_metrics(self, filepath: str):
        """导出指标到文件"""
        data = {
            "statistics": self.get_statistics(),
            "tool_statistics": self.get_tool_statistics(),
            "recent_metrics": [
                {
                    "operation": m.operation,
                    "duration": m.duration,
                    "timestamp": m.timestamp.isoformat(),
                    "success": m.success,
                    "error": m.error,
                    "metadata": m.metadata
                }
                for m in list(self.metrics)[-100:]  # 最近100条
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def clear_metrics(self):
        """清除指标数据"""
        self.metrics.clear()
        self.tool_stats.clear()


class ErrorRecovery:
    """错误恢复机制"""
    
    def __init__(self):
        self.recovery_strategies: Dict[str, List[Callable]] = defaultdict(list)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.max_retries = 3
        
    def register_recovery(self, error_pattern: str, strategy: Callable):
        """注册恢复策略"""
        self.recovery_strategies[error_pattern].append(strategy)
        
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Optional[Any]:
        """处理错误并尝试恢复"""
        error_type = type(error).__name__
        error_message = str(error)
        
        # 记录错误次数
        error_key = f"{error_type}:{context.get('operation', 'unknown')}"
        self.error_counts[error_key] += 1
        
        # 检查是否超过最大重试次数
        if self.error_counts[error_key] > self.max_retries:
            logger.error(f"错误 {error_key} 超过最大重试次数")
            return None
            
        # 查找匹配的恢复策略
        for pattern, strategies in self.recovery_strategies.items():
            if pattern in error_type or pattern in error_message:
                for strategy in strategies:
                    try:
                        logger.info(f"尝试恢复策略: {strategy.__name__}")
                        
                        if asyncio.iscoroutinefunction(strategy):
                            result = await strategy(error, context)
                        else:
                            result = strategy(error, context)
                            
                        if result is not None:
                            # 恢复成功，重置错误计数
                            self.error_counts[error_key] = 0
                            return result
                            
                    except Exception as e:
                        logger.error(f"恢复策略失败: {e}")
                        
        return None
        
    def reset_error_count(self, error_key: str):
        """重置错误计数"""
        self.error_counts[error_key] = 0
        
    def get_error_summary(self) -> Dict[str, int]:
        """获取错误摘要"""
        return dict(self.error_counts)


# 全局监控实例
monitor = PerformanceMonitor()
error_recovery = ErrorRecovery()


# 注册默认错误恢复策略
async def rate_limit_recovery(error: Exception, context: Dict[str, Any]):
    """速率限制恢复"""
    if "rate limit" in str(error).lower():
        logger.info("触发速率限制，等待60秒...")
        await asyncio.sleep(60)
        return True
    return None


async def connection_error_recovery(error: Exception, context: Dict[str, Any]):
    """连接错误恢复"""
    if isinstance(error, (ConnectionError, TimeoutError)):
        logger.info("连接错误，等待5秒后重试...")
        await asyncio.sleep(5)
        return True
    return None


# 注册默认策略
error_recovery.register_recovery("rate", rate_limit_recovery)
error_recovery.register_recovery("Connection", connection_error_recovery)
error_recovery.register_recovery("Timeout", connection_error_recovery)