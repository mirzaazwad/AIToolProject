"""
Logging system for the agent application.
Provides specialized loggers for different components.
"""

from .agent_logger import AgentLogger
from .api_logger import ApiLogger
from .base import BaseLogger
from .tool_logger import ToolLogger

agent_logger = AgentLogger()
api_logger = ApiLogger()
tool_logger = ToolLogger()

__all__ = [
    "BaseLogger",
    "AgentLogger",
    "ApiLogger",
    "ToolLogger",
    "agent_logger",
    "api_logger",
    "tool_logger",
]
