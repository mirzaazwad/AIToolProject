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
        data = {
            "model": OPENAI_MODEL,
            "input": prompt,
            "temperature": 0.7
        }

        try:
            response = self.apiClient.post("/responses", json_data=data)
            response_data = response.json()


            if "output" in response_data and len(response_data["output"]) > 0:
                output = response_data["output"][0]
                if "content" in output and len(output["content"]) > 0:
                    content_item = output["content"][0]
                    if content_item["type"] == "output_text":
                        return content_item["text"]

            raise OpenAIError("No valid response from OpenAI")

        except Exception as e:
            raise OpenAIError(f"Error querying OpenAI: {str(e)}")

    def refine(self, prompt: str) -> ToolPlan:
        data = {
            "model": OPENAI_MODEL,
            "input": self._get_system_prompt(prompt=prompt)
        }

        try:
            response = self.apiClient.post("/responses", json_data=data)
            response_data = response.json()


            if "output" in response_data and len(response_data["output"]) > 0:
                output = response_data["output"][0]
                if "content" in output and len(output["content"]) > 0:
                    content_item = output["content"][0]
                    if content_item["type"] == "output_text":
                        content = content_item["text"].strip()

                        json_match = re.search(r'\[.*\]', content, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(0)
                            return ToolPlan.from_json_string(json_str)
                        else:
                            return ToolPlan.from_json_string(content)


            return ToolPlan(suggestions=[])

        except Exception as e:
            raise OpenAIError(f"Error refining prompt to obtain tool suggestions: {str(e)}")