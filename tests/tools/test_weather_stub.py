"""Tests for Weather Stub Tool"""

import pytest
from tests.stubs.tools.weather import MockWeather
from tests.constants.weather import (
    CITY_TEMPERATURE,
    DEFAULT_WEATHER_METADATA,
)


class TestWeatherStub:
    """Test suite for Weather stub tool."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_weather = MockWeather()

    def test_known_city_paris(self):
        """Test weather stub for Paris."""
        result = self.mock_weather.execute({"city": "Paris"})

        assert result["city"] == "Paris"
        assert result["temp_c"] == 18.0
        assert result["description"] == "cloudy and mild."
        assert result["humidity"] == 60
        assert result["wind_speed"] == 3.2
        assert "18.0°C, cloudy and mild." in result["response"]

    def test_known_city_london(self):
        """Test weather stub for London."""
        result = self.mock_weather.execute({"city": "London"})

        assert result["city"] == "London"
        assert result["temp_c"] == 17.0
        assert result["description"] == "cold and rainy."
        assert result["humidity"] == 70
        assert result["wind_speed"] == 4.1
        assert "17.0°C, cold and rainy." in result["response"]

    def test_known_city_dhaka(self):
        """Test weather stub for Dhaka."""
        result = self.mock_weather.execute({"city": "Dhaka"})

        assert result["city"] == "Dhaka"
        assert result["temp_c"] == 31.0
        assert result["description"] == "humid and hot."
        assert result["humidity"] == 85
        assert result["wind_speed"] == 2.5
        assert "31.0°C, humid and hot." in result["response"]

    def test_known_city_amsterdam(self):
        """Test weather stub for Amsterdam."""
        result = self.mock_weather.execute({"city": "Amsterdam"})

        assert result["city"] == "Amsterdam"
        assert result["temp_c"] == 19.5
        assert result["description"] == "windy and cloudy."
        assert result["humidity"] == 65
        assert result["wind_speed"] == 3.8
        assert "19.5°C, windy and cloudy." in result["response"]

    def test_unknown_city_uses_defaults(self):
        """Test weather stub for unknown city uses default values."""
        result = self.mock_weather.execute({"city": "UnknownCity"})

        assert result["city"] == "UnknownCity"
        assert result["temp_c"] == DEFAULT_WEATHER_METADATA["temp_c"]
        assert result["description"] == DEFAULT_WEATHER_METADATA["description"]
        assert result["humidity"] == DEFAULT_WEATHER_METADATA["humidity"]
        assert result["wind_speed"] == DEFAULT_WEATHER_METADATA["wind_speed"]
        assert (
            f"{DEFAULT_WEATHER_METADATA['temp_c']}°C, {DEFAULT_WEATHER_METADATA['description']}"
            in result["response"]
        )

    def test_case_insensitive_city_matching(self):
        """Test that city matching is case insensitive."""
        test_cases = [
            ("paris", "paris"),
            ("LONDON", "LONDON"),
            ("dHaKa", "dHaKa"),
            ("AMSTERDAM", "AMSTERDAM"),
        ]

        for input_city, expected_city in test_cases:
            result = self.mock_weather.execute({"city": input_city})
            assert result["city"] == expected_city

            expected_temp = float(CITY_TEMPERATURE[input_city.lower()])
            assert result["temp_c"] == expected_temp

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

        expected_keys = [
            "raw",
            "response",
            "temp_c",
            "humidity",
            "description",
            "wind_speed",
            "city",
        ]
        for key in expected_keys:
            assert key in result

        assert isinstance(result["temp_c"], float)
        assert isinstance(result["humidity"], int)
        assert isinstance(result["wind_speed"], float)
        assert isinstance(result["description"], str)
        assert isinstance(result["response"], str)
        assert isinstance(result["city"], str)

    def test_temperature_conversion_consistency(self):
        """Test that temperature conversion is consistent."""
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

        assert result["temp_c"] == DEFAULT_WEATHER_METADATA["temp_c"]
        assert result["description"] == DEFAULT_WEATHER_METADATA["description"]
        assert result["humidity"] == DEFAULT_WEATHER_METADATA["humidity"]
        assert result["wind_speed"] == DEFAULT_WEATHER_METADATA["wind_speed"]

    def test_empty_city_name(self):
        """Test behavior with empty city name."""

        with pytest.raises(ValueError, match="City name cannot be empty"):
            self.mock_weather.execute({"city": ""})

    def test_numeric_temperature_handling(self):
        """Test that both string and numeric temperatures are handled correctly."""

        result_paris = self.mock_weather.execute({"city": "Paris"})
        assert result_paris["temp_c"] == 18.0

        result_london = self.mock_weather.execute({"city": "London"})
        assert result_london["temp_c"] == 17.0

        result_amsterdam = self.mock_weather.execute({"city": "Amsterdam"})
        assert result_amsterdam["temp_c"] == 19.5

    def test_weather_response_object_structure(self):
        """Test that the WeatherResponse object is properly structured."""
        result = self.mock_weather.execute({"city": "Paris"})
        response_text = result["response"]

        assert isinstance(response_text, str)
        assert len(response_text) > 0

        assert "18.0°C" in response_text
        assert "cloudy and mild." in response_text
