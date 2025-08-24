"""Constants for Tools"""

from enum import Enum


class Tool(Enum):
    CALCULATOR = "calculator"
    WEATHER = "weather"
    KNOWLEDGE_BASE = "knowledge_base"
    CURRENCY_CONVERTER = "currency_converter"


WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
CURRENCY_API_URL = "https://api.frankfurter.dev/v1"
