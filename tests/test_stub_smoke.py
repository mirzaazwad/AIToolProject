"""Stub Agent Smoke Tests"""

import pytest
from dotenv import load_dotenv

from tests.utils.stubs.agent import AgentStub as Agent


@pytest.mark.usefixtures("agent_fixture")
class TestStubSmoke:
    """Smoke test suite for Stub Agent."""

    @pytest.fixture(autouse=True)
    def agent_fixture(self):
        """Fixture to provide a Stub Agent instance."""
        load_dotenv()
        self.stub_agent = Agent()

    def test_ada_lovelace(self):
        """Test question about Ada Lovelace."""
        out = self.stub_agent.answer("Who is Ada Lovelace?")
        assert isinstance(out, str)
        assert len(out) > 10
        assert any(
            keyword in out.lower()
            for keyword in ["ada", "lovelace", "mathematician", "computing"]
        )

    def test_unknown_person(self):
        """Test question about an unknown person."""
        out = self.stub_agent.answer("Who is Unknown Person?")
        assert isinstance(out, str)
        assert len(out) > 10
        assert any(
            keyword in out.lower()
            for keyword in [
                "unknown",
                "person",
                "unable",
                "sorry",
                "no",
                "valid",
                "tools",
            ]
        )

    def test_alan_turing(self):
        """Test question about Alan Turing."""
        out = self.stub_agent.answer("Who is Alan Turing?")
        assert isinstance(out, str)
        assert len(out) > 10
        assert any(
            keyword in out.lower()
            for keyword in [
                "alan",
                "turing",
                "mathematician",
                "computer",
                "intelligence",
            ]
        )

    def test_calculator_addition(self):
        """Test calculator addition."""
        out = self.stub_agent.answer("What is 1 + 1?")
        assert isinstance(out, str)
        assert "2" in out or "2.0" in out

    def test_percentage_calculation(self):
        """Test percentage calculation."""
        out = self.stub_agent.answer("What is 12.5% of 243?")
        assert isinstance(out, str)
        assert "30.375" in out or "30" in out

    def test_weather_summary(self):
        """Test weather summary in natural language."""
        out = self.stub_agent.answer("Summarize today's weather in Paris in 3 words.")
        assert isinstance(out, str)
        assert len(out) > 5
        assert any(
            word in out.lower()
            for word in [
                "mild",
                "cloudy",
                "clear",
                "warm",
                "cool",
                "sunny",
                "rainy",
                "weather",
            ]
        )

    def test_contextual_weather_math(self):
        """Test contextual weather-based math calculation."""
        out = self.stub_agent.answer(
            "Add 10 to the average temperature in Paris and London right now."
        )
        assert isinstance(out, str)
        temp_value = float(out.replace("°C", ""))
        assert temp_value == 27.5

    def test_currency_conversion(self):
        """Test currency conversion functionality."""
        out = self.stub_agent.answer("Convert the average of 10 and 20 USD into EUR.")
        assert isinstance(out, str)
        import re

        numbers = re.findall(r"\d+\.?\d*", out)
        if numbers:
            assert float(numbers[0]) > 0
        else:
            assert float(out) > 0
