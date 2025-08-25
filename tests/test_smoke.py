"""Smoke Tests"""

import pytest
from tests.utils.stubs.agent import AgentStub as Agent


@pytest.mark.usefixtures("agent_fixture")
class TestSmoke:
    """Smoke test suite for Agent."""

    @pytest.fixture(autouse=True)
    def agent_fixture(self):
        """Fixture to provide an Agent instance."""
        self.agent = Agent()

    def test_ada_lovelace(self):
        """Test question about Ada Lovelace."""
        out = self.agent.answer("Who is Ada Lovelace?")
        assert (
            out
            == "Ada Lovelace was a 19th-century mathematician regarded as an early computing pioneer for her work on Charles Babbage's Analytical Engine."
        )

    def test_alan_turing(self):
        """Test question about Alan Turing."""
        out = self.agent.answer("Who is Alan Turing?")
        assert (
            out
            == "Alan Turing was a mathematician and logician, widely considered to be the father of theoretical computer science and artificial intelligence."
        )

    def test_calculator_addition(self):
        """Test calculator functionality for addition."""
        out = self.agent.answer("What is 1 + 1?")
        assert out == "2.0"

    def test_percentage_calculation(self):
        """Test percentage calculation."""
        out = self.agent.answer("What is 12.5% of 243?")
        assert out == "30.375"

    def test_weather_summary(self):
        """Test weather summary in natural language."""
        out = self.agent.answer("Summarize today’s weather in Paris in 3 words.")
        assert out.lower() in [
            "mild and cloudy.",
            "cloudy and mild.",
            "partly cloudy skies.",
        ]

    def test_contextual_weather_math(self):
        """Test contextual weather-based math calculation."""
        out = self.agent.answer(
            "Add 10 to the average temperature in Paris and London right now."
        )
        assert out.endswith("°C")
        assert float(out.replace("°C", "")) > 20.0

    def test_currency_conversion(self):
        """Test currency conversion functionality."""
        out = self.agent.answer("Convert the average of 10 and 20 USD into EUR.")
        assert float(out) > 0
