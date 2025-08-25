"""Tests for Weather Stub Tool"""

import pytest
from tests.utils.stubs.tools.weather import MockWeather
from tests.utils.constants.weather import CITY_TEMPERATURE, DEFAULT_WEATHER_METADATA


@pytest.mark.usefixtures("weather_fixture")
class TestWeatherStub:
    """Test suite for Weather stub tool."""

    @pytest.fixture(autouse=True)
    def weather_fixture(self):
        """Fixture that provides a MockWeather instance for each test."""
        self.mock_weather = MockWeather()

    @pytest.mark.parametrize(
        "city, expected",
        [
            ("Paris", {"temp_c": 18.0, "description": "cloudy and mild.", "humidity": 60, "wind_speed": 3.2}),
            ("London", {"temp_c": 17.0, "description": "cold and rainy.", "humidity": 70, "wind_speed": 4.1}),
            ("Dhaka", {"temp_c": 31.0, "description": "humid and hot.", "humidity": 85, "wind_speed": 2.5}),
            ("Amsterdam", {"temp_c": 19.5, "description": "windy and cloudy.", "humidity": 65, "wind_speed": 3.8}),
        ],
    )
    def test_known_cities(self, city, expected):
        """Test weather stub for known cities."""
        result = self.mock_weather.execute({"city": city})

        assert result["city"] == city
        assert result["temp_c"] == expected["temp_c"]
        assert result["description"] == expected["description"]
        assert result["humidity"] == expected["humidity"]
        assert result["wind_speed"] == expected["wind_speed"]
        assert f"{expected['temp_c']}°C, {expected['description']}" in result["response"]

    def test_unknown_city_uses_defaults(self):
        """Test weather stub for unknown city uses default values."""
        result = self.mock_weather.execute({"city": "UnknownCity"})

        assert result["city"] == "UnknownCity"
        for key, value in DEFAULT_WEATHER_METADATA.items():
            assert result[key] == value
        assert f"{DEFAULT_WEATHER_METADATA['temp_c']}°C, {DEFAULT_WEATHER_METADATA['description']}" in result["response"]

    @pytest.mark.parametrize("input_city", ["paris", "LONDON", "dHaKa", "AMSTERDAM"])
    def test_case_insensitive_city_matching(self, input_city):
        """Test that city matching is case insensitive."""
        result = self.mock_weather.execute({"city": input_city})
        assert result["city"] == input_city
        assert result["temp_c"] == float(CITY_TEMPERATURE[input_city.lower()])

    def test_city_with_whitespace(self):
        """Test city names with leading/trailing whitespace."""
        result = self.mock_weather.execute({"city": "  Paris  "})

        assert result["city"] == "Paris"
        assert result["temp_c"] == 18.0
        assert result["description"] == "cloudy and mild."
        assert "Paris" in result["response"]

    def test_response_structure(self):
        """Test that the response has the expected structure."""
        result = self.mock_weather.execute({"city": "Paris"})
        expected_keys = {"raw", "response", "temp_c", "humidity", "description", "wind_speed", "city"}

        assert expected_keys.issubset(result.keys())
        assert isinstance(result["temp_c"], float)
        assert isinstance(result["humidity"], int)
        assert isinstance(result["wind_speed"], float)
        assert isinstance(result["description"], str)
        assert isinstance(result["response"], str)
        assert isinstance(result["city"], str)

    def test_temperature_conversion_consistency(self):
        """Test that temperature conversion is consistent across all cities."""
        for city_key, raw_temp in CITY_TEMPERATURE.items():
            result = self.mock_weather.execute({"city": city_key.title()})
            expected_temp = float(raw_temp)
            assert result["temp_c"] == expected_temp
            assert str(expected_temp) in result["response"]

    def test_weather_response_format(self):
        """Test that the weather response follows the expected format."""
        result = self.mock_weather.execute({"city": "Paris"})
        response = result["response"]

        assert "18.0°C" in response
        assert "cloudy and mild." in response
        assert "°C," in response

    def test_metadata_fallback(self):
        """Test metadata fallback for cities with partial data."""
        result = self.mock_weather.execute({"city": "UnknownTestCity"})
        for key, value in DEFAULT_WEATHER_METADATA.items():
            assert result[key] == value

    def test_empty_city_name(self):
        """Test behavior with empty city name."""
        with pytest.raises(ValueError, match="City name cannot be empty"):
            self.mock_weather.execute({"city": ""})

    @pytest.mark.parametrize(
        "city, expected_temp",
        [("Paris", 18.0), ("London", 17.0), ("Amsterdam", 19.5)],
    )
    def test_numeric_temperature_handling(self, city, expected_temp):
        """Test that both string and numeric temperatures are handled correctly."""
        result = self.mock_weather.execute({"city": city})
        assert result["temp_c"] == expected_temp

    def test_weather_response_object_structure(self):
        """Test that the WeatherResponse object is properly structured."""
        result = self.mock_weather.execute({"city": "Paris"})
        response_text = result["response"]

        assert isinstance(response_text, str)
        assert len(response_text) > 0
        assert "18.0°C" in response_text
        assert "cloudy and mild." in response_text
