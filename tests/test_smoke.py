"""Smoke Tests"""

from tests.stubs.agent import AgentStub as Agent


def test_ada_lovelace():
    out = Agent().answer("Who is Ada Lovelace?")
    assert (
        out
        == "Ada Lovelace was a 19th-century mathematician regarded as an early computing pioneer for her work on Charles Babbage's Analytical Engine."
    )


def test_alan_turing():
    out = Agent().answer("Who is Alan Turing?")
    assert (
        out
        == "Alan Turing was a mathematician and logician, widely considered to be the father of theoretical computer science and artificial intelligence."
    )


def test_calculator_addition():
    out = Agent().answer("What is 1 + 1?")
    assert out == "2.0"


def test_percentage_calculation():
    out = Agent().answer("What is 12.5% of 243?")
    assert out == "30.375"


def test_weather_summary():
    out = Agent().answer("Summarize today’s weather in Paris in 3 words.")
    assert out.lower() in [
        "mild and cloudy.",
        "cloudy and mild.",
        "partly cloudy skies.",
    ]


def test_contextual_weather_math():
    out = Agent().answer(
        "Add 10 to the average temperature in Paris and London right now."
    )
    assert out.endswith("°C")
    assert float(out.replace("°C", "")) > 20.0


def test_currency_conversion():
    out = Agent().answer("Convert the average of 10 and 20 USD into EUR.")
    assert out == "12.9221"
    assert float(out) > 0
