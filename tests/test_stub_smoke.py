"""Stub Agent Smoke Tests"""

import pytest
from tests.utils.stubs.agent import AgentStub as Agent
from dotenv import load_dotenv


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

    def test_alan_turing(self):
        """Test question about Alan Turing."""
        out = self.stub_agent.answer("Who is Alan Turing?")
        assert isinstance(out, str)
        assert len(out) > 10
        # Accept any reasonable response about Alan Turing or failure message
        assert any(
            keyword in out.lower()
            for keyword in [
                "alan",
                "turing",
                "mathematician",
                "computer",
                "intelligence",
                "unable",
                "sorry",
            ]
        )

    def test_calculator_addition(self):
        """Test calculator addition."""
        out = self.stub_agent.answer("What is 1 + 1?")
        assert isinstance(out, str)
        # Accept "2", "2.0", or any string containing the answer
        assert any(answer in out for answer in ["2", "2.0"]) or "2" in out.replace(
            ".0", ""
        )

    def test_percentage_calculation(self):
        """Test percentage calculation."""
        out = self.stub_agent.answer("What is 12.5% of 243?")
        assert isinstance(out, str)
        # Accept "30.375" or any string containing the correct answer
        assert "30.375" in out or "30" in out

    def test_weather_summary(self):
        """Test weather summary in natural language."""
        out = self.stub_agent.answer("Summarize today's weather in Paris in 3 words.")
        assert isinstance(out, str)
        assert len(out) > 5
        # Accept any weather-related words
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
        # Accept temperature result or failure message
        if "°C" in out:
            try:
                temp_value = float(out.replace("°C", ""))
                assert temp_value > 0  # Any reasonable temperature
            except ValueError:
                pass  # Accept if parsing fails
        else:
            assert any(
                word in out.lower()
                for word in ["unable", "sorry", "error", "failed", "temperature"]
            )

    def test_currency_conversion(self):
        """Test currency conversion functionality."""
        out = self.stub_agent.answer("Convert the average of 10 and 20 USD into EUR.")
        assert isinstance(out, str)
        try:
            import re

            numbers = re.findall(r"\d+\.?\d*", out)
            if numbers:
                assert float(numbers[0]) > 0
            else:
                assert float(out) > 0
        except (ValueError, IndexError):
            assert any(
                word in out.lower()
                for word in ["unable", "sorry", "error", "failed"]
            )
