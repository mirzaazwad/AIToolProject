"""Tests for Gemini LLM Strategy"""

import pytest
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv
from src.lib.llm.gemini import GeminiStrategy
from src.lib.errors.llms.gemini import GeminiError
from src.data.schemas.tools.tool import ToolPlan
from src.constants.llm import GEMINI_API_URL, GEMINI_MODEL


@pytest.mark.usefixtures("gemini_fixture")
class TestGeminiStrategy:
    """Test suite for Gemini LLM Strategy."""

    @pytest.fixture(autouse=True)
    def gemini_fixture(self):
        """Fixture that provides a Gemini strategy instance for each test."""
        load_dotenv()
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-api-key"}):
            self.strategy = GeminiStrategy()

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
        """Test Gemini strategy initializes correctly with API key."""
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            strategy = GeminiStrategy()
            assert strategy.apiClient.base_url == GEMINI_API_URL
            assert "X-goog-api-key" in strategy.apiClient.default_headers

    def test_initialization_without_api_key(self):
        """Test Gemini strategy initializes with None API key."""
        with patch.dict(os.environ, {}, clear=True):
            strategy = GeminiStrategy()
            assert strategy.apiClient.base_url == GEMINI_API_URL

    def test_successful_query(self):
        """Test successful query to Gemini API."""
        mock_response_data = {
            "candidates": [{"content": {"parts": [{"text": "The answer is 42"}]}}]
        }
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            result = self.strategy.query("What is the meaning of life?")
            assert result == "The answer is 42"

    def test_query_with_empty_candidates(self):
        """Test query handling when API returns empty candidates."""
        mock_response_data = {"candidates": []}
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            with pytest.raises(GeminiError, match="Error querying Gemini"):
                self.strategy.query("Test query")

    def test_query_with_malformed_response(self):
        """Test query handling with malformed API response."""
        mock_response_data = {"invalid": "structure"}
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            with pytest.raises(GeminiError, match="Error querying Gemini"):
                self.strategy.query("Test query")

    def test_query_api_error(self):
        """Test query handling when API call fails."""
        with patch.object(
            self.strategy.apiClient, "post", side_effect=Exception("API Error")
        ):
            with pytest.raises(GeminiError, match="Error querying Gemini"):
                self.strategy.query("Test query")

    def test_successful_refine_with_json_array(self):
        """Test successful refine operation returning valid tool plan."""
        mock_response_data = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '[{"tool": "calculator", "args": {"expr": "2+2"}}]'
                            }
                        ]
                    }
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
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": 'Here are the tools: [{"tool": "weather", "args": {"city": "Paris"}}] for your query.'
                            }
                        ]
                    }
                }
            ]
        }
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            result = self.strategy.refine("What's the weather in Paris?")
            assert isinstance(result, ToolPlan)
            assert len(result.suggestions) >= 0

    def test_refine_with_empty_candidates(self):
        """Test refine handling when API returns empty candidates."""
        mock_response_data = {"candidates": []}
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            result = self.strategy.refine("Test query")
            assert isinstance(result, ToolPlan)
            assert len(result.suggestions) == 0

    def test_refine_api_error(self):
        """Test refine handling when API call fails."""
        with patch.object(
            self.strategy.apiClient, "post", side_effect=Exception("API Error")
        ):
            with pytest.raises(GeminiError, match="Error refining prompt"):
                self.strategy.refine("Test query")

    def test_refine_with_invalid_json(self):
        """Test refine handling with invalid JSON response."""
        mock_response_data = {
            "candidates": [{"content": {"parts": [{"text": "invalid json response"}]}}]
        }
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            with pytest.raises(GeminiError, match="Error refining prompt"):
                self.strategy.refine("Test query")

    def test_query_request_structure(self):
        """Test that query sends correct request structure."""
        mock_response = self._mock_response(
            200, {"candidates": [{"content": {"parts": [{"text": "response"}]}}]}
        )

        with patch.object(
            self.strategy.apiClient, "post", return_value=mock_response
        ) as mock_post:
            self.strategy.query("test prompt")

            args, kwargs = mock_post.call_args
            assert args[0] == f"/{GEMINI_MODEL}:generateContent"
            assert "json_data" in kwargs
            request_data = kwargs["json_data"]
            assert "contents" in request_data
            assert request_data["contents"][0]["parts"][0]["text"] == "test prompt"

    def test_refine_request_structure(self):
        """Test that refine sends correct request structure."""
        mock_response = self._mock_response(
            200, {"candidates": [{"content": {"parts": [{"text": "[]"}]}}]}
        )

        with patch.object(
            self.strategy.apiClient, "post", return_value=mock_response
        ) as mock_post:
            self.strategy.refine("test prompt")

            args, kwargs = mock_post.call_args
            assert args[0] == f"/{GEMINI_MODEL}:generateContent"
            assert "json_data" in kwargs
            request_data = kwargs["json_data"]
            assert "contents" in request_data
            assert "test prompt" in request_data["contents"][0]["parts"][0]["text"]

    def test_system_prompt_generation(self):
        """Test that system prompt is generated correctly."""
        system_prompt = self.strategy._get_system_prompt("What is 2+2?")

        assert "What is 2+2?" in system_prompt
        assert "Role:" in system_prompt
        assert "Context:" in system_prompt
        assert "Response Format:" in system_prompt
        assert "JSON" in system_prompt

    def test_multiple_parts_handling(self):
        """Test handling of responses with multiple parts."""
        mock_response_data = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "first part"}, {"text": "second part"}]
                    }
                }
            ]
        }
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            result = self.strategy.query("test")
            assert result == "first part"

    def test_error_message_preservation(self):
        """Test that original error messages are preserved in exceptions."""
        original_error = "Connection timeout"

        with patch.object(
            self.strategy.apiClient, "post", side_effect=Exception(original_error)
        ):
            with pytest.raises(GeminiError) as exc_info:
                self.strategy.query("test")

            assert original_error in str(exc_info.value)

    def test_refine_with_no_parts(self):
        """Test refine handling when response has no parts."""
        mock_response_data = {"candidates": [{"content": {"parts": []}}]}
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            result = self.strategy.refine("Test query")
            assert isinstance(result, ToolPlan)
            assert len(result.suggestions) == 0

    def test_refine_with_whitespace_response(self):
        """Test refine handling with whitespace-only response."""
        mock_response_data = {
            "candidates": [{"content": {"parts": [{"text": "   \n\t   "}]}}]
        }
        mock_response = self._mock_response(200, mock_response_data)

        with patch.object(self.strategy.apiClient, "post", return_value=mock_response):
            with pytest.raises(GeminiError, match="Error refining prompt"):
                self.strategy.refine("Test query")

    def test_api_key_header_setting(self):
        """Test that API key is correctly set in headers."""
        test_key = "test-gemini-key-123"
        with patch.dict(os.environ, {"GEMINI_API_KEY": test_key}):
            strategy = GeminiStrategy()
            assert strategy.apiClient.default_headers["X-goog-api-key"] == test_key

    def test_content_type_header(self):
        """Test that content type header is correctly set."""
        assert self.strategy.apiClient.default_headers["Content-Type"] == "application/json"
