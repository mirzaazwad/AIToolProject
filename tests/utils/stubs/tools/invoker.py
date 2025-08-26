"""Stub for ToolInvoker"""

import time

from src.constants.tools import Tool
from src.lib.errors.tools.invoker import InvokerError
from src.lib.loggers import tool_logger
from src.lib.tools.base import Action, ToolInvokerBase
from src.lib.tools.calculator import Calculator
from src.lib.tools.currency_converter import CurrencyConverter
from src.lib.tools.knowledge_base import KnowledgeBase

from .weather import MockWeather as Weather


class StubToolInvoker(ToolInvokerBase):
    def __init__(self):
        self._action: Action | None = None
        self._current_tool: str | None = None

    def set_action(self, tool_type: str) -> None:
        self._current_tool = tool_type
        if tool_type == Tool.CALCULATOR.value:
            self._action = Calculator()
        elif tool_type == Tool.WEATHER.value:
            self._action = Weather()
        elif tool_type == Tool.KNOWLEDGE_BASE.value:
            self._action = KnowledgeBase()
        elif tool_type == Tool.CURRENCY_CONVERTER.value:
            self._action = CurrencyConverter()
        else:
            raise ValueError(f"Unknown tool type: {tool_type}")

    def execute(self, args: dict) -> str:
        if self._action is None:
            raise RuntimeError("No tool action set. Call set_action() first.")

        tool_logger.log_tool_call(self._current_tool, args)
        start_time = time.time()
        try:
            result = self._action.execute(args)
            execution_time = time.time() - start_time
            tool_logger.log_tool_success(self._current_tool, result, execution_time)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            error_type = type(e).__name__
            tool_logger.log_tool_failure(self._current_tool, str(e), error_type)
            raise InvokerError(f"Tool execution failed: {str(e)}") from e
