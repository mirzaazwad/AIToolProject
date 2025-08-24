"""Tests for LLM Stub"""
import pytest

from tests.stubs.llm import StubLLMStrategy
from tests.stubs.agent import AgentStub
from data.schemas.tool import ToolPlan

@pytest.fixture
def llm():
    return StubLLMStrategy()

@pytest.fixture
def agent():
    return AgentStub()

def test_refine_calculator(llm):
    plan = llm.refine("2 + 3 * 4")
    assert isinstance(plan, ToolPlan)
    assert plan.suggestions[0].tool == "calculator"
    assert plan.suggestions[0].args["expr"] == "2 + 3 * 4"

def test_refine_weather(llm):
    plan = llm.refine("Tell me the weather in Dhaka")
    assert plan.suggestions[0].tool == "weather"
    assert plan.suggestions[0].args["city"] == "Dhaka"

def test_refine_knowledge_base(llm):
    plan = llm.refine("Who is Ada Lovelace?")
    assert plan.suggestions[0].tool == "knowledge_base"
    assert "ada lovelace" in plan.suggestions[0].args["query"]

def test_refine_currency(llm):
    plan = llm.refine("convert 5 EUR to USD")
    tools = [s.tool for s in plan.suggestions]
    assert any(t in ["calculator", "currency_converter"] for t in tools)

def test_agent_execute_tools_calculator(agent, llm):
    plan = llm.refine("10 + 20")
    responses = agent.execute_tools(plan)
    calc = [r for r in responses if r["tool"] == "calculator"]
    assert calc
    assert calc[0]["success"] is True

def test_agent_execute_tools_weather(agent, llm):
    plan = llm.refine("Weather in London")
    responses = agent.execute_tools(plan)
    weather = [r for r in responses if r["tool"] == "weather"]
    assert weather
    assert "London" in weather[0]["args"]["city"]

def test_agent_execute_dependent_calculator(agent, llm):
    plan = llm.refine("add 5 to the average temperature in Paris and London")
    responses = agent.execute_tools(plan)
    calc = [r for r in responses if r["tool"] == "calculator"]
    assert calc
    assert calc[0]["success"]
