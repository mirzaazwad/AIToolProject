"""Stub for Weather Tool"""

from typing import Any, Dict
from src.data.schemas.tools.weather import (
    WeatherRequest,
    WeatherResponse,
    MainWeatherData,
    WindData,
    WeatherCondition,
    SysData,
)
from src.lib.tools.base import Action
from tests.constants.weather import (
    CITY_TEMPERATURE,
    WEATHER_METADATA,
    DEFAULT_WEATHER_METADATA,
)


class MockWeather(Action):
    """
    MockWeather mirrors the real Weather tool's output format by creating a WeatherResponse
    object populated with synthetic data and returning WeatherResponse.get_formatted_response().
    """

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        req = WeatherRequest(**args)
        city_key = req.city.strip().lower()

        raw_temp = None

        if city_key in CITY_TEMPERATURE:
            raw_temp = CITY_TEMPERATURE[city_key]
            temp_c = float(raw_temp)
            meta = WEATHER_METADATA.get(city_key, {})
            humidity = meta.get("humidity", 50)
            description = meta.get(
                "description", DEFAULT_WEATHER_METADATA["description"]
            )
            wind_speed = meta.get("wind_speed", DEFAULT_WEATHER_METADATA["wind_speed"])
        else:
            raw_temp = str(DEFAULT_WEATHER_METADATA["temp_c"])
            temp_c = float(DEFAULT_WEATHER_METADATA["temp_c"])
            humidity = DEFAULT_WEATHER_METADATA["humidity"]
            description = DEFAULT_WEATHER_METADATA["description"]
            wind_speed = DEFAULT_WEATHER_METADATA["wind_speed"]

        main = MainWeatherData(
            temp=round(temp_c + 273.15, 2),
            pressure=1013,
            humidity=humidity,
            temp_min=round((temp_c - 1) + 273.15, 2),
            temp_max=round((temp_c + 1) + 273.15, 2),
        )

        wind = WindData(speed=wind_speed, deg=None)

        weather_condition = WeatherCondition(
            id=800, main="Clear", description=description
        )
        sys = SysData(country="XX", sunrise=0, sunset=0)

        response = WeatherResponse(
            name=req.city.title(),
            weather=[weather_condition],
            main=main,
            wind=wind,
            clouds=None,
            sys=sys,
            cod=200,
        )

        return {
            "raw": raw_temp,
            "response": response.get_formatted_response(),
            "temp_c": temp_c,
            "humidity": humidity,
            "description": description,
            "wind_speed": wind_speed,
            "city": req.city,
        }
