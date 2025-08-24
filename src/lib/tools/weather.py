"""Weather Tool"""
from .base import Action
from ..api import ApiClient
from ...constants.tools import WEATHER_API_URL
from ...data.schemas.tools.weather import WeatherRequest, WeatherResponse
from ..errors.tools.weather import (
    WeatherAPIError,
    CityNotFoundError,
    WeatherRequestError,
    WeatherConfigurationError
)
from os import getenv

class Weather(Action):
    """Weather tool using OpenWeatherMap API."""

    def __init__(self):
        self.apiClient = ApiClient(base_url=WEATHER_API_URL)
        self.api_key = getenv("WEATHER_API_KEY")
        if not self.api_key:
            raise WeatherConfigurationError("WEATHER_API_KEY environment variable is required")

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
                raise WeatherAPIError(f"Weather API error: {raw_response.status_code} - {raw_response.text}")


            response = WeatherResponse(**raw_response.json())


            return response.get_formatted_response()
        except ValueError as e:
            raise WeatherRequestError(f"Invalid request data: {str(e)}")