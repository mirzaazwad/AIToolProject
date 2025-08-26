from ..llm.gemini import GeminiStrategy
from ..tools.tool_invoker import ToolInvoker
from .base import Agent


class GeminiAgent(Agent):
    """Agent using Gemini LLM for tool suggestion and fusion."""

    def __init__(self):
        super().__init__(llm_strategy=GeminiStrategy(), tool_invoker=ToolInvoker())
