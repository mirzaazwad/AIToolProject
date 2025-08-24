"""Tool Invoker using Command Pattern"""
from .calculator import Calculator
from .weather import Weather
from .knowledge_base import KnowledgeBase
from .currency_converter import CurrencyConverter
from .base import ToolInvokerBase
from constants.tools import Tool
from lib.loggers import tool_logger
import time
from lib.errors.tools.invoker import InvokerError

class ToolInvoker(ToolInvokerBase):
    """Invoker class for executing tools using Command Pattern"""

    def set_action(self, tool_type: str) -> None:
        """Set the action/tool to be executed."""
        self.__current_tool = tool_type

        if tool_type == Tool.CALCULATOR.value:
            self.__action = Calculator()
        elif tool_type == Tool.WEATHER.value:
            self.__action = Weather()
        elif tool_type == Tool.KNOWLEDGE_BASE.value:
            self.__action = KnowledgeBase()
        elif tool_type == Tool.CURRENCY_CONVERTER.value:
            self.__action = CurrencyConverter()
        else:
            raise ValueError(f"Unknown tool type: {tool_type}")

    def execute(self, args: dict) -> str:
        """Execute the current tool with logging."""
        if not hasattr(self, '_ToolInvoker__action'):
            raise RuntimeError("No tool action set. Call set_action() first.")

        tool_logger.log_tool_call(self.__current_tool, args)

        start_time = time.time()
        try:
            result = self.__action.execute(args)
            execution_time = time.time() - start_time

            tool_logger.log_tool_success(self.__current_tool, result, execution_time)
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            error_type = type(e).__name__

            tool_logger.log_tool_failure(self.__current_tool, str(e), error_type)
            raise InvokerError(f"Tool execution failed: {str(e)}") from e
        


    