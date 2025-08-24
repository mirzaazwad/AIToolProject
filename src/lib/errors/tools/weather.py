"""Weather tool specific exceptions."""


class WeatherError(Exception):
    """Base exception for weather tool errors."""

    def __init__(self, message: str = "Weather tool error occurred"):
        self.message = message
        super().__init__(self.message)


class WeatherAPIError(WeatherError):
    """Exception raised for weather API related errors."""

    def __init__(self, message: str = "Weather API error"):
        self.message = message
        super().__init__(self.message)


class CityNotFoundError(WeatherError):
    """Exception raised when a city is not found."""

    def __init__(self, message: str = "City not found"):
        self.message = message
        super().__init__(self.message)


class WeatherRequestError(WeatherError):
    """Exception raised for invalid weather requests."""

    def __init__(self, message: str = "Invalid weather request"):
        self.message = message
        super().__init__(self.message)


class WeatherConfigurationError(WeatherError):
    """Exception raised for weather tool configuration errors."""

    def __init__(self, message: str = "Weather tool configuration error"):
        self.message = message
        super().__init__(self.message)
