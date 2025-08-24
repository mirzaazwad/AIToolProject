from .base import Agent
from lib.llm.gemini import GeminiStrategy
from lib.tools.tool_invoker import ToolInvoker

class GeminiAgent(Agent):
    """Agent using Gemini LLM for tool suggestion and fusion."""

    def __init__(self):
        super().__init__(llm_strategy=GeminiStrategy(), tool_invoker=ToolInvoker())

