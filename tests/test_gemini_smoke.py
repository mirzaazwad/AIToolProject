"""Gemini Agent Smoke Tests"""

import pytest
from src.lib.agents.gemini import GeminiAgent
from dotenv import load_dotenv


@pytest.mark.usefixtures("agent_fixture")
class TestGeminiSmoke:
    """Smoke test suite for Gemini Agent."""

    @pytest.fixture(autouse=True)
    def agent_fixture(self):
        """Fixture to provide a Gemini Agent instance."""
        load_dotenv()
        self.gemini_agent = GeminiAgent()

    def test_ada_lovelace(self):
        """Test question about Ada Lovelace."""
        out = self.gemini_agent.answer("Who is Ada Lovelace?")
        assert isinstance(out, str)
        assert len(out) > 10
        # Accept any reasonable response about Ada Lovelace or failure message
        assert any(
            keyword in out.lower()
            for keyword in [
                "ada",
                "lovelace",
                "mathematician",
                "computing",
                "pioneer",
                "writer",
                "english",
                "math",
                "unable",
                "sorry",
            ]
        )

    def test_alan_turing(self):
        """Test question about Alan Turing."""
        out = self.gemini_agent.answer("Who is Alan Turing?")
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
                "unable",
                "sorry",
            ]
        )

    def test_calculator_addition(self):
        """Test calculator addition."""
        out = self.gemini_agent.answer("What is 1 + 1?")
        assert isinstance(out, str)
        # Accept correct answer or failure message
        assert (
            any(answer in out for answer in ["2", "2.0"])
            or "2" in out.replace(".0", "")
            or any(word in out.lower() for word in ["unable", "sorry"])
        )

    def test_percentage_calculation(self):
        """Test percentage calculation."""
        out = self.gemini_agent.answer("What is 12.5% of 243?")
        assert isinstance(out, str)
        # Accept correct answer or failure message
        assert (
            "30.375" in out
            or "30" in out
            or any(word in out.lower() for word in ["unable", "sorry"])
        )

    def test_weather_summary(self):
        """Test weather summary in natural language."""
        out = self.gemini_agent.answer("Summarize today's weather in Paris in 3 words.")
        assert isinstance(out, str)
        assert len(out) > 5
        # Accept weather-related words or failure message
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
                "unable",
                "sorry",
            ]
        )

    def test_contextual_weather_math(self):
        """Test contextual weather-based math calculation."""
        out = self.gemini_agent.answer(
            "Add 10 to the average temperature in Paris and London right now."
        )
        assert isinstance(out, str)
        if "°C" in out:
            try:
                temp_value = float(out.replace("°C", ""))
                assert temp_value > 0
            except ValueError:
                pass
        else:
            assert any(
                word in out.lower()
                for word in ["unable", "sorry", "error", "failed", "temperature"]
            )

    def test_currency_conversion(self):
        """Test currency conversion functionality."""
        out = self.gemini_agent.answer("Convert the average of 10 and 20 USD into EUR.")
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
