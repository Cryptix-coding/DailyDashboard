import requests
from typing import Any, Optional
from config import Config


def get_current_weather() -> Optional[dict[str, Any]]:
    """
    Fetch current weather and a 2-day forecast (Tomorrow & Day after tomorrow)
    from the Open-Meteo API.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": Config.LATITUDE,
        "longitude": Config.LONGITUDE,
        "current": "temperature_2m,weather_code",
        "daily": "weather_code,temperature_2m_max",
        "timezone": "auto",
        "forecast_days": 3
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # 1. Current weather
        current = data.get("current", {})
        temp = round(current.get("temperature_2m", 0))
        code = int(current.get("weather_code", 0))
        description, icon = Config.WEATHER_CODES.get(code, ("Unbekannt", "🌤️"))

        # 2. Forecast for Tomorrow (index 1) and Day after tomorrow (index 2)
        daily = data.get("daily", {})
        daily_codes = daily.get("weather_code", [])
        daily_temps = daily.get("temperature_2m_max", [])

        forecast = []
        labels = ["Morgen", "Übermorgen"]

        for idx, label in enumerate(labels, start=1):
            if idx < len(daily_codes) and idx < len(daily_temps):
                f_code = int(daily_codes[idx])
                f_temp = round(daily_temps[idx])
                f_desc, f_icon = Config.WEATHER_CODES.get(f_code, ("Unbekannt", "🌤️"))
                forecast.append({
                    "label": label,
                    "icon": f_icon,
                    "temp": f_temp,
                    "description": f_desc
                })

        return {
            "location": Config.LOCATION_NAME,
            "temperature": temp,
            "description": description,
            "condition": description,
            "icon": icon,
            "forecast": forecast
        }
    except Exception as error:
        print(f"[WeatherService] Error fetching weather data: {error}")
        return None