from .base import Agent
from ..llm.openai import OpenAIStrategy
from ..tools.tool_invoker import ToolInvoker

class OpenAIAgent(Agent):
    """Agent using OpenAI ChatGPT LLM for tool suggestion and fusion."""

    def __init__(self):
        super().__init__(llm_strategy=OpenAIStrategy(), tool_invoker=ToolInvoker())
