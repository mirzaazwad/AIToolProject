"""Tests for LLM Stub"""

import pytest

from src.data.schemas.tools.tool import ToolPlan
from tests.utils.stubs.agent import AgentStub
from tests.utils.stubs.llm import StubLLMStrategy


@pytest.mark.usefixtures("llm_fixture", "agent_fixture")
class TestLLMStub:
    """Test suite for LLM Stub and Agent tool execution."""

    @pytest.fixture(autouse=True)
    def llm_fixture(self):
        """Fixture to provide an LLM stub instance."""
        self.llm = StubLLMStrategy()

    @pytest.fixture(autouse=True)
    def agent_fixture(self):
        """Fixture to provide an Agent stub instance."""
        self.agent = AgentStub()

    def test_refine_calculator(self):
        """Test refining a calculator expression into a tool plan."""
        plan = self.llm.refine("2 + 3 * 4")
        assert isinstance(plan, ToolPlan)
        assert plan.suggestions[0].tool == "calculator"
        assert plan.suggestions[0].args["expr"] == "2 + 3 * 4"

    def test_refine_weather(self):
        """Test refining a weather query into a tool plan."""
        plan = self.llm.refine("Tell me the weather in Dhaka")
        assert plan.suggestions[0].tool == "weather"
        assert plan.suggestions[0].args["city"] == "Dhaka"

    def test_refine_knowledge_base(self):
        """Test refining a knowledge base query."""
        plan = self.llm.refine("Who is Ada Lovelace?")
        assert plan.suggestions[0].tool == "knowledge_base"
        assert "ada lovelace" in plan.suggestions[0].args["query"]

    def test_refine_currency(self):
        """Test refining a currency conversion request."""
        plan = self.llm.refine("convert 5 EUR to USD")
        tools = [s.tool for s in plan.suggestions]
        assert any(t in ["calculator", "currency_converter"] for t in tools)

    def test_agent_execute_tools_calculator(self):
        """Test agent execution of a calculator tool plan."""
        plan = self.llm.refine("10 + 20")
        responses = self.agent.execute_tools(plan)
        calc = [r for r in responses if r["tool"] == "calculator"]
        assert calc
        assert calc[0]["success"] is True

    def test_agent_execute_tools_weather(self):
        """Test agent execution of a weather tool plan."""
        plan = self.llm.refine("Weather in London")
        responses = self.agent.execute_tools(plan)
        weather = [r for r in responses if r["tool"] == "weather"]
        assert weather
        assert "London" in weather[0]["args"]["city"]

    def test_agent_execute_dependent_calculator(self):
        """Test agent execution of dependent calculator plan with weather."""
        plan = self.llm.refine("add 5 to the average temperature in Paris and London")
        responses = self.agent.execute_tools(plan)
        calc = [r for r in responses if r["tool"] == "calculator"]
        assert calc
        assert calc[0]["success"]
