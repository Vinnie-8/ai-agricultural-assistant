import requests
from langchain_core.tools import tool

from app.config import settings

WEATHER_API_URL = "https://api.weatherapi.com/v1/forecast.json"


@tool
def get_weather_forecast(location: str = "auto:ip") -> str:
    """
    Get the current weather and 3-day rain forecast for the farmer's
    location. Use this when the farmer asks about weather, rain, or
    whether it's a good time to spray fungicide/pesticide (spraying
    right before rain washes off treatment and wastes it).

    Args:
        location: The farmer's location. Pass "auto:ip" (the default) to
            use their detected location, or a specific city/region name
            if the farmer has mentioned one in the conversation.
    """
    try:
        response = requests.get(
            WEATHER_API_URL,
            params={
                "key": settings.WEATHER_API_KEY,
                "q": location,
                "days": 3,
                "aqi": "no",
                "alerts": "no",
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Weather lookup failed: {e}"

    data = response.json()

    if "error" in data:
        return f"Weather lookup failed: {data['error'].get('message', 'unknown error')}"

    loc = data["location"]
    current = data["current"]
    forecast_days = data["forecast"]["forecastday"]

    lines = [
        f"Location: {loc['name']}, {loc['region']}, {loc['country']}",
        f"Current: {current['condition']['text']}, {current['temp_c']}°C, "
        f"{current['precip_mm']}mm precipitation right now",
        "",
        "3-day forecast:",
    ]

    for day in forecast_days:
        d = day["day"]
        lines.append(
            f"  {day['date']}: {d['condition']['text']}, "
            f"chance of rain {d['daily_chance_of_rain']}%, "
            f"total precipitation {d['totalprecip_mm']}mm, "
            f"max/min {d['maxtemp_c']}/{d['mintemp_c']}°C"
        )

    return "\n".join(lines)