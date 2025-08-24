"""Weather Tool"""

from .base import Action
from ..api import ApiClient
from ...constants.tools import WEATHER_API_URL
from ...data.schemas.tools.weather import WeatherRequest, WeatherResponse
from ..errors.tools.weather import (
    WeatherAPIError,
    CityNotFoundError,
    WeatherRequestError,
    WeatherConfigurationError,
)
from os import getenv


class Weather(Action):
    """Weather tool using OpenWeatherMap API."""

    def __init__(self):
        self.apiClient = ApiClient(base_url=WEATHER_API_URL)
        self.api_key = getenv("WEATHER_API_KEY")
        if not self.api_key:
            raise WeatherConfigurationError(
                "WEATHER_API_KEY environment variable is required"
            )

    def execute(self, args: dict) -> str:
        """
        Execute weather lookup.

        Args:
            args: Dictionary containing 'city' key

        Returns:
            Formatted weather information string
        """
        try:
            request = WeatherRequest(**args)

            params = request.to_query_params()
            params["appid"] = self.api_key

            raw_response = self.apiClient.get("", params=params)

            if raw_response.status_code == 404:
                raise CityNotFoundError(f"City '{request.city}' not found")
            elif raw_response.status_code != 200:
                raise WeatherAPIError(
                    f"Weather API error: {raw_response.status_code} - {raw_response.text}"
                )

            try:
                response = WeatherResponse(**raw_response.json())
            except ValueError as e:
                raise WeatherAPIError(f"Invalid weather data format: {str(e)}")

            return response.get_formatted_response()

        except (CityNotFoundError, WeatherAPIError):
            raise
        except ValueError as e:
            error_msg = str(e)
            if "Field required" in error_msg and "city" in error_msg:
                raise WeatherRequestError("City parameter is required")
            elif "City name cannot be empty" in error_msg:
                raise WeatherRequestError("City name cannot be empty")
            else:
                raise WeatherRequestError(f"Invalid request data: {error_msg}")
        except Exception as e:
            raise WeatherAPIError(f"Weather request failed: {str(e)}")
