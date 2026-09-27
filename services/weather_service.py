import requests
from typing import Optional
from config import Config


def get_current_weather() -> Optional[dict[str, str | int]]:
    """
    Fetch current weather data from the Open-Meteo API.
    Returns None if the network request fails or returns invalid data.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={Config.LATITUDE}&longitude={Config.LONGITUDE}"
        f"&current_weather=true"
    )

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        current = data["current_weather"]
        weather_code = current["weathercode"]
        description, icon_symbol = Config.WEATHER_CODES.get(
            weather_code, ("Bewölkt", "⛅")
        )

        return {
            "location": Config.LOCATION_NAME,
            "temperature": round(current["temperature"]),
            "description": description,
            "icon": icon_symbol
        }
    except (requests.RequestException, KeyError, ValueError) as error:
        print(f"[WeatherService] Error fetching weather data: {error}")
        return None