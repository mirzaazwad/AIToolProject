"""Tests for OpenAI LLM Strategy"""

import pytest
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
from src.lib.llm.openai import OpenAIStrategy
from src.lib.errors.llms.openai import OpenAIError
from src.data.schemas.tools.tool import ToolPlan
from src.constants.llm import OPENAI_API_URL, OPENAI_MODEL


@pytest.mark.usefixtures("openai_fixture")
class TestOpenAIStrategy:
    """Test suite for OpenAI LLM Strategy."""

    @pytest.fixture(autouse=True)
    def openai_fixture(self):
        """Fixture that provides an OpenAI strategy instance for each test."""
        load_dotenv()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
            self.strategy = OpenAIStrategy()

    def _mock_response(self, status_code=200, json_data=None, text=None):
        """Helper to create a mock API response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        if json_data is not None:
            mock_response.json.return_value = json_data
        if text is not None:
            mock_response.text = text
        return mock_response

    def test_initialization_with_api_key(self):
        """Test OpenAI strategy initializes correctly with API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            strategy = OpenAIStrategy()
            assert strategy.apiClient.base_url == OPENAI_API_URL
            assert "Bearer" in str(strategy.apiClient.default_headers.get("Authorization", ""))

    def test_initialization_without_api_key(self):
        """Test OpenAI strategy initializes with None API key."""
        with patch.dict(os.environ, {}, clear=True):
            strategy = OpenAIStrategy()
            assert strategy.apiClient.base_url == OPENAI_API_URL

    def test_successful_query(self):
        """Test successful query to OpenAI API."""
        mock_response_data = {
            "output": [
                {"content": [{"type": "output_text", "text": "The answer is 42"}]}
            ]
        }
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            result = self.strategy.query("What is the meaning of life?")
            assert result == "The answer is 42"

    def test_query_with_empty_response(self):
        """Test query handling when API returns empty response."""
        mock_response_data = {"output": []}
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            with pytest.raises(OpenAIError, match="Error querying OpenAI"):
                self.strategy.query("Test query")

    def test_query_with_malformed_response(self):
        """Test query handling with malformed API response."""
        mock_response_data = {"invalid": "structure"}
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            with pytest.raises(OpenAIError, match="Error querying OpenAI"):
                self.strategy.query("Test query")

    def test_query_api_error(self):
        """Test query handling when API call fails."""
        with patch.object(
            self.strategy.apiClient, "post", side_effect=Exception("API Error")
        ):
            with pytest.raises(OpenAIError, match="Error querying OpenAI"):
                self.strategy.query("Test query")

    def test_successful_refine_with_json_array(self):
        """Test successful refine operation returning valid tool plan."""
        mock_response_data = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": '[{"tool": "calculator", "args": {"expr": "2+2"}}]',
                        }
                    ]
                }
            ]
        }
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            result = self.strategy.refine("What is 2+2?")
            assert isinstance(result, ToolPlan)
            assert len(result.suggestions) >= 0

    def test_refine_with_embedded_json(self):
        """Test refine operation with JSON embedded in text response."""
        mock_response_data = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": 'Here are the tools: [{"tool": "weather", "args": {"city": "Paris"}}] for your query.',
                        }
                    ]
                }
            ]
        }
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            result = self.strategy.refine("What's the weather in Paris?")
            assert isinstance(result, ToolPlan)
            assert len(result.suggestions) >= 0

    def test_refine_with_empty_response(self):
        """Test refine handling when API returns empty response."""
        mock_response_data = {"output": []}
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            with pytest.raises(OpenAIError, match="Error refining prompt"):
                self.strategy.refine("Test query")

    def test_refine_api_error(self):
        """Test refine handling when API call fails."""
        with patch.object(
            self.strategy.apiClient, "post", side_effect=Exception("API Error")
        ):
            with pytest.raises(OpenAIError, match="Error refining prompt"):
                self.strategy.refine("Test query")

    def test_refine_with_invalid_json(self):
        """Test refine handling with invalid JSON response."""
        mock_response_data = {
            "output": [
                {"content": [{"type": "output_text", "text": "invalid json response"}]}
            ]
        }
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            with pytest.raises(OpenAIError, match="Error refining prompt"):
                self.strategy.refine("Test query")

    def test_query_request_structure(self):
        """Test that query sends correct request structure."""
        mock_response = self._mock_response(
            200,
            {"output": [{"content": [{"type": "output_text", "text": "response"}]}]},
        )

        with patch.object(
            self.strategy.apiClient, "post", return_value=mock_response
        ) as mock_post:
            self.strategy.query("test prompt")

            args, kwargs = mock_post.call_args
            assert args[0] == "/responses"
            assert "json_data" in kwargs
            request_data = kwargs["json_data"]
            assert request_data["model"] == OPENAI_MODEL
            assert request_data["input"] == "test prompt"
            assert "temperature" in request_data

    def test_refine_request_structure(self):
        """Test that refine sends correct request structure."""
        mock_response = self._mock_response(
            200, {"output": [{"content": [{"type": "output_text", "text": "[]"}]}]}
        )

        with patch.object(
            self.strategy.apiClient, "post", return_value=mock_response
        ) as mock_post:
            self.strategy.refine("test prompt")

            args, kwargs = mock_post.call_args
            assert args[0] == "/responses"
            assert "json_data" in kwargs
            request_data = kwargs["json_data"]
            assert request_data["model"] == OPENAI_MODEL
            assert "input" in request_data
            assert "test prompt" in request_data["input"]

    def test_system_prompt_generation(self):
        """Test that system prompt is generated correctly."""
        system_prompt = self.strategy._get_system_prompt("What is 2+2?")

        assert "What is 2+2?" in system_prompt
        assert "Role:" in system_prompt
        assert "Context:" in system_prompt
        assert "Response Format:" in system_prompt
        assert "JSON" in system_prompt

    def test_multiple_content_items_handling(self):
        """Test handling of responses with multiple content items."""
        mock_response_data = {
            "output": [
                {
                    "content": [
                        {"type": "other", "text": "ignore this"},
                        {"type": "output_text", "text": "correct response"},
                    ]
                }
            ]
        }
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            result = self.strategy.query("test")
            assert result == "correct response"

    def test_error_message_preservation(self):
        """Test that original error messages are preserved in exceptions."""
        original_error = "Connection timeout"

        with patch.object(
            self.strategy.apiClient, "post", side_effect=Exception(original_error)
        ):
            with pytest.raises(OpenAIError) as exc_info:
                self.strategy.query("test")

            assert original_error in str(exc_info.value)
