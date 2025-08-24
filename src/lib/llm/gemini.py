"""Strategy Pattern Application for Google Gemini"""

from .base import LLMStrategy
from ..api import ApiClient
from ...data.schemas.tools.tool import ToolPlan
from ...constants.llm import GEMINI_API_URL, GEMINI_MODEL
from ..errors.llms.gemini import GeminiError
from os import getenv
import re


class GeminiStrategy(LLMStrategy):
    """LLM strategy using Google Gemini."""

    def __init__(self):
        self.apiClient = ApiClient(base_url=GEMINI_API_URL)
        self.apiClient.set_default_headers(
            {
                "Content-Type": "application/json",
                "X-goog-api-key": getenv("GEMINI_API_KEY"),
            }
        )

    def query(self, prompt: str) -> str:
        try:
            data = {"contents": [{"parts": [{"text": prompt}]}]}
            response = self.apiClient.post(
                f"/{GEMINI_MODEL}:generateContent", json_data=data
            )
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise GeminiError(f"Error querying Gemini: {str(e)}")

    def refine(self, prompt: str) -> ToolPlan:
        data = {
            "contents": [{"parts": [{"text": self._get_system_prompt(prompt=prompt)}]}]
        }

        try:
            response = self.apiClient.post(
                f"/{GEMINI_MODEL}:generateContent", json_data=data
            )
            response_data = response.json()
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                content = response_data["candidates"][0]["content"]
                if "parts" in content and len(content["parts"]) > 0:
                    text_response = content["parts"][0]["text"].strip()
                    json_match = re.search(r"\[.*\]", text_response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        return ToolPlan.from_json_string(json_str)
                    else:
                        return ToolPlan.from_json_string(text_response)

            return ToolPlan(suggestions=[])

        except Exception as e:
            raise GeminiError(
                f"Error refining prompt to obtain tool suggestions: {str(e)}"
            )
