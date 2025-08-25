"""Tests for Weather Tool"""

import pytest
from unittest.mock import Mock, patch
from src.lib.tools.weather import Weather
from src.lib.errors.tools.weather import (
    WeatherAPIError,
    CityNotFoundError,
    WeatherRequestError,
    WeatherConfigurationError,
)


@pytest.mark.usefixtures("weather_fixture")
class TestWeather:
    """Test suite for Weather tool."""

    @pytest.fixture(autouse=True)
    def weather_fixture(self):
        """Fixture to create Weather instance with patched API key."""
        with patch.dict("os.environ", {"WEATHER_API_KEY": "test_api_key"}):
            self.weather = Weather()

    def _mock_response(self, status_code=200, json_data=None, text=""):
        """Helper to build a mock API response."""
        mock = Mock()
        mock.status_code = status_code
        mock.text = text
        if json_data is not None:
            mock.json.return_value = json_data
        return mock

    def test_successful_weather_request(self):
        """Test successful weather data retrieval."""
        json_data = {
            "name": "London",
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky"}],
            "main": {
                "temp": 288.15,
                "pressure": 1013,
                "humidity": 65,
                "temp_min": 287.15,
                "temp_max": 289.15,
            },
            "wind": {"speed": 3.5, "deg": 180},
            "clouds": {"all": 20},
            "sys": {"country": "GB", "sunrise": 1640000000, "sunset": 1640030000},
            "cod": 200,
        }

        with patch.object(self.weather.apiClient, "get", return_value=self._mock_response(200, json_data)):
            result = self.weather.execute({"city": "London"})
            assert "15.0°C" in result
            assert "clear sky" in result

    @pytest.mark.parametrize(
        "city, temp_kelvin, description",
        [
            ("Paris", 291.15, "partly cloudy"),
            ("Tokyo", 298.15, "sunny"),
            ("New York", 285.15, "rainy"),
        ],
    )
    def test_weather_with_different_cities(self, city, temp_kelvin, description):
        """Test weather requests for multiple cities."""
        json_data = {
            "name": city,
            "weather": [{"id": 800, "main": "Clear", "description": description}],
            "main": {
                "temp": temp_kelvin,
                "pressure": 1013,
                "humidity": 60,
                "temp_min": temp_kelvin - 2,
                "temp_max": temp_kelvin + 2,
            },
            "wind": {"speed": 2.5, "deg": 90},
            "clouds": {"all": 10},
            "sys": {"country": "XX", "sunrise": 1640000000, "sunset": 1640030000},
            "cod": 200,
        }
        with patch.object(self.weather.apiClient, "get", return_value=self._mock_response(200, json_data)):
            result = self.weather.execute({"city": city})
            expected_temp = round(temp_kelvin - 273.15, 1)
            assert f"{expected_temp}°C" in result
            assert description in result

    @pytest.mark.parametrize(
        "params, expected_error, match",
        [
            ({}, WeatherRequestError, "City parameter is required"),
            ({"city": ""}, WeatherRequestError, "City name cannot be empty"),
            ({"city": "   "}, WeatherRequestError, "City name cannot be empty"),
        ],
    )
    def test_invalid_city_inputs(self, params, expected_error, match):
        """Test missing, empty, and whitespace-only city names."""
        with pytest.raises(expected_error, match=match):
            self.weather.execute(params)

    def test_city_not_found(self):
        """Test error when city is not found."""
        with patch.object(
            self.weather.apiClient, "get", return_value=self._mock_response(404, text="city not found")
        ):
            with pytest.raises(CityNotFoundError, match="City 'InvalidCity' not found"):
                self.weather.execute({"city": "InvalidCity"})

    def test_api_key_missing(self):
        """Test error when API key is missing."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(
                WeatherConfigurationError,
                match="WEATHER_API_KEY environment variable is required",
            ):
                Weather()

    @pytest.mark.parametrize(
        "status_code, text",
        [
            (500, "Internal server error"),
            (401, "Invalid API key"),
        ],
    )
    def test_api_error_responses(self, status_code, text):
        """Test handling of API server and unauthorized errors."""
        with patch.object(
            self.weather.apiClient, "get", return_value=self._mock_response(status_code, text=text)
        ):
            with pytest.raises(WeatherAPIError, match="Weather API error"):
                self.weather.execute({"city": "London"})

    def test_malformed_api_response(self):
        """Test handling of malformed API responses."""
        bad_json = {"invalid": "response"}
        with patch.object(self.weather.apiClient, "get", return_value=self._mock_response(200, bad_json)):
            with pytest.raises(WeatherAPIError, match="Invalid weather data format"):
                self.weather.execute({"city": "London"})

    def test_network_error(self):
        """Test handling of network errors."""
        with patch.object(self.weather.apiClient, "get", side_effect=Exception("Network error")):
            with pytest.raises(WeatherAPIError, match="Weather request failed"):
                self.weather.execute({"city": "London"})

    def test_weather_with_optional_fields_missing(self):
        """Test weather response when optional fields are missing."""
        json_data = {
            "name": "TestCity",
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky"}],
            "main": {
                "temp": 288.15,
                "pressure": 1013,
                "humidity": 65,
                "temp_min": 287.15,
                "temp_max": 289.15,
            },
            "sys": {"country": "XX", "sunrise": 1640000000, "sunset": 1640030000},
            "cod": 200,
        }
        with patch.object(self.weather.apiClient, "get", return_value=self._mock_response(200, json_data)):
            result = self.weather.execute({"city": "TestCity"})
            assert "15.0°C" in result
            assert "clear sky" in result

    @pytest.mark.parametrize(
        "temp_kelvin, expected_celsius",
        [
            (233.15, -40.0),
            (323.15, 50.0),
            (273.15, 0.0),
        ],
    )
    def test_extreme_temperatures(self, temp_kelvin, expected_celsius):
        """Test weather with extreme temperature values."""
        json_data = {
            "name": "ExtremeCity",
            "weather": [{"id": 800, "main": "Clear", "description": "clear"}],
            "main": {
                "temp": temp_kelvin,
                "pressure": 1013,
                "humidity": 50,
                "temp_min": temp_kelvin - 1,
                "temp_max": temp_kelvin + 1,
            },
            "wind": {"speed": 1.0, "deg": 0},
            "clouds": {"all": 0},
            "sys": {"country": "XX", "sunrise": 1640000000, "sunset": 1640030000},
            "cod": 200,
        }
        with patch.object(self.weather.apiClient, "get", return_value=self._mock_response(200, json_data)):
            result = self.weather.execute({"city": "ExtremeCity"})
            assert f"{expected_celsius}°C" in result

    @pytest.mark.parametrize("city_name", ["london", "LONDON", "London", "LoNdOn"])
    def test_city_name_case_insensitive(self, city_name):
        """Test that city names are handled case-insensitively."""
        json_data = {
            "name": "London",
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky"}],
            "main": {
                "temp": 288.15,
                "pressure": 1013,
                "humidity": 65,
                "temp_min": 287.15,
                "temp_max": 289.15,
            },
            "wind": {"speed": 3.5, "deg": 180},
            "clouds": {"all": 20},
            "sys": {"country": "GB", "sunrise": 1640000000, "sunset": 1640030000},
            "cod": 200,
        }
        with patch.object(self.weather.apiClient, "get", return_value=self._mock_response(200, json_data)):
            result = self.weather.execute({"city": city_name})
            assert "15.0°C" in result
            assert "clear sky" in result
