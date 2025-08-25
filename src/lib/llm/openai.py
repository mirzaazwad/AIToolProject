"""Strategy Pattern Application for OpenAI"""

from .base import LLMStrategy
from ..api import ApiClient
from ...data.schemas.tools.tool import ToolPlan
from ...constants.llm import OPENAI_API_URL, OPENAI_MODEL
from ..errors.llms.openai import OpenAIError
from os import getenv
import re


class OpenAIStrategy(LLMStrategy):
    """LLM strategy using OpenAI ChatGPT."""

    def __init__(self):
        self.apiClient = ApiClient(base_url=OPENAI_API_URL)
        self.apiClient.set_auth_header(getenv("OPENAI_API_KEY"), "Bearer")
        self.apiClient.set_default_headers({"Content-Type": "application/json"})

    def query(self, prompt: str) -> str:
        data = {"model": OPENAI_MODEL, "input": prompt, "temperature": 0.7}

        try:
            response = self.apiClient.post("/responses", json_data=data)
            return self._extract_text_response(response.json())
        except Exception as e:
            raise OpenAIError(f"Error querying OpenAI: {str(e)}")

    def refine(self, prompt: str) -> ToolPlan:
        data = {"model": OPENAI_MODEL, "input": self._get_system_prompt(prompt=prompt)}

        try:
            response = self.apiClient.post("/responses", json_data=data)
            content = self._extract_text_response(response.json(), default="").strip()

            if not content:
                return ToolPlan(suggestions=[])

            return self._parse_tool_plan(content)

        except Exception as e:
            raise OpenAIError(
                f"Error refining prompt to obtain tool suggestions: {str(e)}"
            )

    def _extract_text_response(self, response_data: dict, default: str = None) -> str:
        """Extract text from OpenAI-like response JSON."""
        outputs = response_data.get("output", [])
        if not outputs:
            raise OpenAIError("No output found in OpenAI response")

        content_items = outputs[0].get("content", [])
        for item in content_items:
            if item.get("type") == "output_text":
                return item.get("text", default)
        raise OpenAIError("No text response found in OpenAI output")

    def _parse_tool_plan(self, content: str) -> ToolPlan:
        """Parse raw model output into a ToolPlan."""
        json_match = re.search(r"\[.*\]", content, re.DOTALL)
        json_str = json_match.group(0) if json_match else content
        return ToolPlan.from_json_string(json_str)
