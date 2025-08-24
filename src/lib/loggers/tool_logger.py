"""
Tool-specific logger for tracking tool executions and results.
"""

from .base import BaseLogger
from ...data.schemas.logging.metrics import ToolMetrics
from typing import Union


class ToolLogger(BaseLogger):
    """Logger specialized for tool operations."""

    def __init__(self, level: str = "INFO"):
        super().__init__("tool", "tool.log", level)

        if not hasattr(self, "metrics"):
            self.metrics = ToolMetrics()

    def log_tool_call(
        self, tool_name: str, args: dict[str, Union[str, float, int]]
    ) -> None:
        """Log a tool call attempt."""
        self.metrics.tool_calls += 1
        self._update_tool_usage(tool_name)
        if tool_name not in self.metrics.execution_sequence:
            self.metrics.execution_sequence.append(tool_name)

        self.info(f"CALLING: {tool_name} with args: {args}")

    def log_tool_success(
        self, tool_name: str, result: str, execution_time: float = 0.0
    ) -> None:
        """Log successful tool execution."""
        self.metrics.successful_calls += 1

        result_str = str(result)
        if len(result_str) > 200:
            result_str = result_str[:200] + "..."

        self.info(f"SUCCESS: {tool_name} completed in {execution_time:.2f}s")
        self.debug(f"Result: {result_str}")

    def log_tool_failure(
        self, tool_name: str, error: str, error_type: str = "Unknown"
    ) -> None:
        """Log failed tool execution."""
        self.metrics.failed_calls += 1

        self.error(f"FAILED: {tool_name} - {error_type}: {error}")

    def _update_tool_usage(self, tool_name: str) -> None:
        """Update tool usage statistics."""
        if tool_name not in self.metrics.tool_usage:
            self.metrics.tool_usage[tool_name] = 0
        self.metrics.tool_usage[tool_name] += 1

    def get_metrics(self) -> ToolMetrics:
        """Get current tool metrics."""
        return self.metrics.model_copy()
