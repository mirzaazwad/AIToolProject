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


class TestWeather:
    """Test suite for Weather tool."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict("os.environ", {"WEATHER_API_KEY": "test_api_key"}):
            self.weather = Weather()

    def test_successful_weather_request(self):
        """Test successful weather data retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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

        with patch.object(self.weather.apiClient, "get", return_value=mock_response):
            result = self.weather.execute({"city": "London"})
            assert "15.0°C" in result
            assert "clear sky" in result

    def test_weather_with_different_cities(self):
        """Test weather requests for different cities."""
        cities_data = [
            ("Paris", 291.15, "partly cloudy"),
            ("Tokyo", 298.15, "sunny"),
            ("New York", 285.15, "rainy"),
        ]

        for city, temp_kelvin, description in cities_data:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
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

            with patch.object(
                self.weather.apiClient, "get", return_value=mock_response
            ):
                result = self.weather.execute({"city": city})
                expected_temp = round(temp_kelvin - 273.15, 1)
                assert f"{expected_temp}°C" in result
                assert description in result

    def test_missing_city_parameter(self):
        """Test error when city parameter is missing."""
        with pytest.raises(WeatherRequestError, match="City parameter is required"):
            self.weather.execute({})

    def test_empty_city_parameter(self):
        """Test error when city parameter is empty."""
        with pytest.raises(WeatherRequestError, match="City name cannot be empty"):
            self.weather.execute({"city": ""})

    def test_whitespace_only_city(self):
        """Test error when city parameter contains only whitespace."""
        with pytest.raises(WeatherRequestError, match="City name cannot be empty"):
            self.weather.execute({"city": "   "})

    def test_city_not_found(self):
        """Test error when city is not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "city not found"

        with patch.object(self.weather.apiClient, "get", return_value=mock_response):
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

    def test_api_server_error(self):
        """Test handling of API server errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"

        with patch.object(self.weather.apiClient, "get", return_value=mock_response):
            with pytest.raises(WeatherAPIError, match="Weather API error"):
                self.weather.execute({"city": "London"})

    def test_api_unauthorized(self):
        """Test handling of unauthorized API access."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Invalid API key"

        with patch.object(self.weather.apiClient, "get", return_value=mock_response):
            with pytest.raises(WeatherAPIError, match="Weather API error"):
                self.weather.execute({"city": "London"})

    def test_malformed_api_response(self):
        """Test handling of malformed API responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "response"}

        with patch.object(self.weather.apiClient, "get", return_value=mock_response):
            with pytest.raises(WeatherAPIError, match="Invalid weather data format"):
                self.weather.execute({"city": "London"})

    def test_network_error(self):
        """Test handling of network errors."""
        with patch.object(
            self.weather.apiClient, "get", side_effect=Exception("Network error")
        ):
            with pytest.raises(WeatherAPIError, match="Weather request failed"):
                self.weather.execute({"city": "London"})

    def test_weather_with_optional_fields_missing(self):
        """Test weather response when optional fields are missing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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

        with patch.object(self.weather.apiClient, "get", return_value=mock_response):
            result = self.weather.execute({"city": "TestCity"})
            assert "15.0°C" in result
            assert "clear sky" in result

    def test_extreme_temperatures(self):
        """Test weather with extreme temperature values."""
        extreme_temps = [
            (233.15, -40.0),
            (323.15, 50.0),
            (273.15, 0.0),
        ]

        for temp_kelvin, temp_celsius in extreme_temps:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
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

            with patch.object(
                self.weather.apiClient, "get", return_value=mock_response
            ):
                result = self.weather.execute({"city": "ExtremeCity"})
                assert f"{temp_celsius}°C" in result

    def test_city_name_case_insensitive(self):
        """Test that city names are handled case-insensitively."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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

        city_variations = ["london", "LONDON", "London", "LoNdOn"]

        for city_name in city_variations:
            with patch.object(
                self.weather.apiClient, "get", return_value=mock_response
            ):
                result = self.weather.execute({"city": city_name})
                assert "15.0°C" in result
                assert "clear sky" in result
