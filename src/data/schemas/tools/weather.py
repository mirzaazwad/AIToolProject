"""Schema for Weather API"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class WeatherRequest(BaseModel):
    city: str = Field(..., description="City name for weather information")

    @field_validator("city")
    @classmethod
    def validate_city(cls, v):
        if not v or not v.strip():
            raise ValueError("City name cannot be empty")
        return v.strip()

    def to_query_params(self) -> dict[str, str]:
        """Convert to query parameters for API request."""
        return {"q": self.city}


class WeatherCondition(BaseModel):
    """Weather condition details."""

    id: int = Field(..., description="Weather condition ID")
    main: str = Field(..., description="Group of weather parameters")
    description: str = Field(..., description="Weather condition description")


class MainWeatherData(BaseModel):
    """Main weather data."""

    temp: float = Field(..., description="Temperature in Kelvin")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    humidity: int = Field(..., description="Humidity percentage")
    temp_min: float = Field(..., description="Minimum temperature in Kelvin")
    temp_max: float = Field(..., description="Maximum temperature in Kelvin")


class WindData(BaseModel):
    """Wind data."""

    speed: float = Field(..., description="Wind speed in meter/sec")
    deg: Optional[int] = Field(None, description="Wind direction in degrees")


class CloudsData(BaseModel):
    """Clouds data."""

    all: int = Field(..., description="Cloudiness percentage")


class SysData(BaseModel):
    """System data."""

    country: str = Field(..., description="Country code")
    sunrise: int = Field(..., description="Sunrise time in Unix timestamp")
    sunset: int = Field(..., description="Sunset time in Unix timestamp")


class WeatherResponse(BaseModel):
    """Weather API response."""

    name: str = Field(..., description="City name")
    weather: list[WeatherCondition] = Field(..., description="Weather conditions")
    main: MainWeatherData = Field(..., description="Main weather data")
    wind: Optional[WindData] = Field(None, description="Wind data")
    clouds: Optional[CloudsData] = Field(None, description="Clouds data")
    sys: SysData = Field(..., description="System data")
    cod: int = Field(..., description="Response code")

    def get_temperature_celsius(self) -> float:
        """Convert temperature from Kelvin to Celsius."""
        return round(self.main.temp - 273.15, 1)

    def get_description(self) -> str:
        """Get weather description."""
        if self.weather:
            return self.weather[0].description
        return "No description available"

    def get_formatted_response(self) -> str:
        """Get formatted weather response."""
        temp_c = self.get_temperature_celsius()
        description = self.get_description()
        humidity = self.main.humidity

        response = (
            f"Weather in {self.name}: {temp_c}°C, {description}, humidity {humidity}%"
        )

        if self.wind:
            response += f", wind speed {self.wind.speed} m/s"

        return response
