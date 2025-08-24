"""Abstract Base Classes for Tools and Invoker using Command Pattern"""

from abc import ABC, abstractmethod


class Action(ABC):
    """Abstract base class for tool actions using Command Pattern"""

    @abstractmethod
    def execute(self, args: dict) -> str:
        pass


class ToolInvokerBase(ABC):
    """Abstract invoker base class for executing tools using Command Pattern"""

    _action: Action
    _current_tool: str

    @abstractmethod
    def set_action(self, tool_type: str) -> None:
        """Set the action/tool to be executed."""
        pass

    @abstractmethod
    def execute(self, args: dict) -> str:
        """Execute the current tool with logging."""
        pass
