"""Tests for OpenAI Agent"""

import pytest
import os
from unittest.mock import patch
from dotenv import load_dotenv
from src.lib.agents.openai import OpenAIAgent
from src.lib.llm.openai import OpenAIStrategy
from src.lib.tools.tool_invoker import ToolInvoker
from src.data.schemas.tools.tool import ToolPlan, ToolSuggestion
from src.data.schemas.tools.tool_response import ToolResponse
from src.constants.messages import FAILED_AGENT_MESSAGE


@pytest.mark.usefixtures("openai_agent_fixture")
class TestOpenAIAgent:
    """Test suite for OpenAI Agent."""

    @pytest.fixture(autouse=True)
    def openai_agent_fixture(self):
        """Fixture that provides an OpenAI agent instance for each test."""
        load_dotenv()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-api-key"}):
            self.agent = OpenAIAgent()

    def _create_mock_tool_plan(self, suggestions=None):
        """Helper to create a mock tool plan."""
        if suggestions is None:
            suggestions = [
                ToolSuggestion(tool="calculator", args={"expr": "2+2"}, depends_on=[])
            ]
        return ToolPlan(suggestions=suggestions)

    def _create_mock_tool_response(
        self, tool="calculator", result="4", success=True, error=None
    ):
        """Helper to create a mock tool response."""
        return ToolResponse(
            tool=tool,
            args={"expr": "2+2"} if tool == "calculator" else {"city": "Paris"},
            result=result,
            success=success,
            error=error,
        )

    def test_initialization(self):
        """Test OpenAI agent initializes correctly."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            agent = OpenAIAgent()
            assert isinstance(agent.llm_strategy, OpenAIStrategy)
            assert isinstance(agent.tool_invoker, ToolInvoker)

    def test_successful_simple_query(self):
        """Test successful processing of a simple query."""
        mock_tool_plan = self._create_mock_tool_plan()

        with patch.object(
            self.agent.llm_strategy, "refine", return_value=mock_tool_plan
        ), patch.object(
            self.agent.llm_strategy, "query", return_value="The answer is 4"
        ), patch.object(
            self.agent.tool_invoker, "set_action"
        ), patch.object(
            self.agent.tool_invoker, "execute", return_value="4"
        ):

            result = self.agent.answer("What is 2+2?")
            assert isinstance(result, str)
            assert len(result) > 0
            assert result != FAILED_AGENT_MESSAGE

    def test_query_with_multiple_tools(self):
        """Test query processing with multiple tool suggestions."""
        suggestions = [
            ToolSuggestion(tool="weather", args={"city": "Paris"}, depends_on=[]),
            ToolSuggestion(tool="weather", args={"city": "London"}, depends_on=[]),
        ]
        mock_tool_plan = self._create_mock_tool_plan(suggestions)

        with patch.object(
            self.agent.llm_strategy, "refine", return_value=mock_tool_plan
        ), patch.object(
            self.agent.llm_strategy, "query", return_value="Paris: 18°C, London: 15°C"
        ), patch.object(
            self.agent.tool_invoker, "set_action"
        ), patch.object(
            self.agent.tool_invoker, "execute", side_effect=["18°C", "15°C"]
        ):

            result = self.agent.answer("What's the weather in Paris and London?")
            assert isinstance(result, str)
            assert len(result) > 0
            assert result != FAILED_AGENT_MESSAGE

    def test_query_with_tool_failure(self):
        """Test query processing when a tool fails."""
        mock_tool_plan = self._create_mock_tool_plan()

        with patch.object(
            self.agent.llm_strategy, "refine", return_value=mock_tool_plan
        ), patch.object(
            self.agent.llm_strategy, "query", return_value="Unable to calculate"
        ), patch.object(
            self.agent.tool_invoker, "set_action"
        ), patch.object(
            self.agent.tool_invoker, "execute", side_effect=Exception("Tool error")
        ):

            result = self.agent.answer("What is 2+2?")
            assert isinstance(result, str)
            assert len(result) > 0

    def test_query_with_llm_refine_failure(self):
        """Test query processing when LLM refine fails."""
        with patch.object(
            self.agent.llm_strategy, "refine", side_effect=Exception("LLM error")
        ):
            result = self.agent.answer("What is 2+2?")
            assert result == FAILED_AGENT_MESSAGE

    def test_query_with_llm_query_failure(self):
        """Test query processing when LLM query fails."""
        mock_tool_plan = self._create_mock_tool_plan()

        with patch.object(
            self.agent.llm_strategy, "refine", return_value=mock_tool_plan
        ), patch.object(
            self.agent.llm_strategy, "query", side_effect=Exception("LLM error")
        ), patch.object(
            self.agent.tool_invoker, "set_action"
        ), patch.object(
            self.agent.tool_invoker, "execute", return_value="4"
        ):

            result = self.agent.answer("What is 2+2?")
            assert result == FAILED_AGENT_MESSAGE

    def test_empty_tool_plan(self):
        """Test processing with empty tool plan."""
        empty_tool_plan = ToolPlan(suggestions=[])

        with patch.object(
            self.agent.llm_strategy, "refine", return_value=empty_tool_plan
        ), patch.object(
            self.agent.llm_strategy, "query", return_value="No tools needed"
        ):

            result = self.agent.answer("Hello")
            assert isinstance(result, str)
            assert len(result) > 0
            assert result != FAILED_AGENT_MESSAGE

    def test_preprocess_query(self):
        """Test query preprocessing."""
        processed = self.agent.preprocess_query("  WHAT IS 2+2?  ")
        assert processed == "what is 2+2?"

    def test_postprocess_responses(self):
        """Test response postprocessing."""
        responses = [
            self._create_mock_tool_response("calculator", "4", True),
            self._create_mock_tool_response("weather", "18°C", True),
        ]
        processed = self.agent.postprocess_responses(responses)
        assert len(processed) == 2
        assert all(isinstance(r, ToolResponse) for r in processed)

    def test_tool_execution_order(self):
        """Test that multiple tools are executed correctly."""
        suggestions = [
            ToolSuggestion(tool="weather", args={"city": "Paris"}, depends_on=[]),
            ToolSuggestion(
                tool="knowledge_base", args={"query": "Paris"}, depends_on=[]
            ),
        ]
        mock_tool_plan = self._create_mock_tool_plan(suggestions)

        execution_order = []

        def mock_set_action(tool):
            execution_order.append(tool)

        with patch.object(
            self.agent.llm_strategy, "refine", return_value=mock_tool_plan
        ), patch.object(
            self.agent.llm_strategy, "query", return_value="Result"
        ), patch.object(
            self.agent.tool_invoker, "set_action", side_effect=mock_set_action
        ), patch.object(
            self.agent.tool_invoker, "execute", side_effect=["18°C", "Paris info"]
        ):

            self.agent.answer("Tell me about Paris weather and facts")

            assert "weather" in execution_order
            assert "knowledge_base" in execution_order

    def test_error_handling_preserves_original_message(self):
        """Test that error handling preserves original error information."""
        original_error = "Specific API error"

        from src.lib.loggers import agent_logger

        with patch.object(
            self.agent.llm_strategy, "refine", side_effect=Exception(original_error)
        ), patch.object(agent_logger, "log_query_failure") as mock_log:

            result = self.agent.answer("test query")
            assert result == FAILED_AGENT_MESSAGE

            mock_log.assert_called_once()
            args = mock_log.call_args[0]
            assert original_error in args[1]  

    def test_successful_logging(self):
        """Test that successful queries are logged correctly."""
        from src.lib.loggers import agent_logger
        mock_tool_plan = self._create_mock_tool_plan()

        with patch.object(
            self.agent.llm_strategy, "refine", return_value=mock_tool_plan
        ), patch.object(
            self.agent.llm_strategy, "query", return_value="Success"
        ), patch.object(
            self.agent.tool_invoker, "set_action"
        ), patch.object(
            self.agent.tool_invoker, "execute", return_value="4"
        ), patch.object(
            agent_logger, "log_query_success"
        ) as mock_log:

            self.agent.answer("What is 2+2?")

            mock_log.assert_called_once()
            args = mock_log.call_args[0]
            assert args[0] == "What is 2+2?"  
            assert args[1] == "Success"  
            assert isinstance(args[2], float)  

    def test_tool_plan_logging(self):
        """Test that tool plans are logged correctly."""
        from src.lib.loggers import agent_logger
        mock_tool_plan = self._create_mock_tool_plan()

        with patch.object(
            self.agent.llm_strategy, "refine", return_value=mock_tool_plan
        ), patch.object(
            self.agent.llm_strategy, "query", return_value="Success"
        ), patch.object(
            self.agent.tool_invoker, "set_action"
        ), patch.object(
            self.agent.tool_invoker, "execute", return_value="4"
        ), patch.object(
            agent_logger, "log_tool_plan"
        ) as mock_log:

            self.agent.answer("What is 2+2?")

            mock_log.assert_called_once()
            logged_plan = mock_log.call_args[0][0]
            assert isinstance(logged_plan, list)
            assert len(logged_plan) > 0
