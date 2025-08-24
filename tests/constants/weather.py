"""Constants for Weather mocking"""

CITY_TEMPERATURE = {
        "paris": "18",
        "london": 17.0,
        "dhaka": 31,
        "amsterdam": "19.5"
    }

WEATHER_METADATA = {
        "paris": {"description": "cloudy and mild.", "humidity": 60, "wind_speed": 3.2},
        "london": {"description": "cold and rainy.", "humidity": 70, "wind_speed": 4.1},
        "dhaka": {"description": "humid and hot.", "humidity": 85, "wind_speed": 2.5},
        "amsterdam": {"description": "windy and cloudy.", "humidity": 65, "wind_speed": 3.8},
    }

DEFAULT_WEATHER_METADATA = {"description": "mild and cloudy", "humidity": 50, "wind_speed": 2.0, "temp_c": 20.0}