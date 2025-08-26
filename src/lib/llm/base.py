"""Abstract Base Class for LLM Strategies"""

from abc import ABC, abstractmethod

from ...constants.llm import (SYSTEM_PROMPT_CONTEXT, TOOL_SUGGESTION_EXAMPLES,
                              TOOL_SYSTEM_ROLE)
from ...constants.messages import TOOL_SUGGESTION_FORMAT
from ...data.schemas.tools.tool import ToolPlan
from ..api import ApiClient


class LLMStrategy(ABC):
    """Abstract base class for LLM strategies using Strategy Pattern"""

    apiClient: ApiClient

    @abstractmethod
    def query(self, prompt: str) -> str:
        """
        Make a basic query to OpenAI/Gemini using the relevant endpoints.

        Args:
            prompt: The user's query

        Returns:
            str: The response from OpenAI
        """
        pass

    @abstractmethod
    def refine(self, prompt: str) -> ToolPlan:
        """
        Refine a prompt to suggest appropriate tools for answering the query.

        Args:
            prompt: The user's query

        Returns:
            ToolPlan: A structured plan with tool suggestions
        """
        pass

    def _get_system_prompt(self, prompt: str) -> str:
        """
        Get the system prompt for the LLM.
        """

        system_prompt = f"""
        Role:
        {TOOL_SYSTEM_ROLE}

        Context:
        {SYSTEM_PROMPT_CONTEXT}

        Response Format: Return ONLY a valid JSON array of tool suggestions in this exact format:
        {TOOL_SUGGESTION_FORMAT}

        IMPORTANT: When multiple tools are suggested, always place the calculator tool LAST in the array. Calculator tool can take results from other tools as input using 'depends_on' key.

        Examples:
        {TOOL_SUGGESTION_EXAMPLES}

        Prompt: {prompt}
        """
        return system_prompt
