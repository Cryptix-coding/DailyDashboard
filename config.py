import os
from dotenv import load_dotenv

# Load environment variables from the local .env file
load_dotenv()


class Config:
    """Central configuration class for the application."""

    # Server configuration
    DEBUG: bool = os.getenv("DEBUG_MODE", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", 5000))

    # Location settings (defaults to Schaidt if .env is not configured)
    LOCATION_NAME: str = os.getenv("LOCATION_NAME", "Schaidt")
    LATITUDE: float = float(os.getenv("LATITUDE", 49.0583))
    LONGITUDE: float = float(os.getenv("LONGITUDE", 8.0833))

    # Calendar settings (Outlook ICS feed)
    CALENDAR_ICS_URL: str = os.getenv("CALENDAR_ICS_URL", "")

    # German localization constants (independent of the host OS locale)
    WEEKDAYS: list[str] = [
        "Montag", "Dienstag", "Mittwoch", "Donnerstag",
        "Freitag", "Samstag", "Sonntag"
    ]
    MONTHS: list[str] = [
        "", "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ]

    # Mapping of WMO Weather Interpretation Codes to German descriptions and weather symbols
    WEATHER_CODES: dict[int, tuple[str, str]] = {
        0: ("Sonnig & Klar", "☀️"),
        1: ("Überwiegend heiter", "🌤️"),
        2: ("Leicht bewölkt", "⛅"),
        3: ("Bedeckt", "☁️"),
        45: ("Nebelig", "🌫️"),
        48: ("Raureif-Nebel", "🌫️"),
        51: ("Leichter Nieselregen", "🌦️"),
        53: ("Nieselregen", "🌦️"),
        55: ("Starker Nieselregen", "🌧️"),
        61: ("Leichter Regen", "🌦️"),
        63: ("Regen", "🌧️"),
        65: ("Starker Regen", "🌧️"),
        71: ("Leichter Schneefall", "🌨️"),
        73: ("Schneefall", "❄️"),
        75: ("Starker Schneefall", "❄️"),
        80: ("Regenschauer", "🌦️"),
        81: ("Kräftige Schauer", "🌧️"),
        82: ("Starke Schauer", "⛈️"),
        95: ("Gewitter", "🌩️"),
        96: ("Gewitter mit Hagel", "⛈️"),
        99: ("Starkes Gewitter", "⛈️")
    }

    # Waste categories: (Display text with colored dot, list of trigger keywords)
    WASTE_TYPES: list[tuple[str, list[str]]] = [
        ("⚫ Restmüll (schwarze Tonne)", ["restmüll", "restmuell", "schwarz"]),
        ("🟤 Biomüll (braune Tonne)", ["biomüll", "biomuell", "bio müll", "bio-müll", "bio", "braun"]),
        ("🟢 Papier (grüne Tonne)", ["papier", "altpapier", "grün", "gruen"]),
        ("🟡 Gelber Sack", ["gelber sack", "geleber sack", "gelbe tonne", "gelb", "plastik", "plastick"]),
        ("⚪ Glasbox", ["glasbox", "glas box", "glas-box", "altglas", "glas"]),
    ]

    # General fallback keywords if an event just says "Müll" or "Sperrmüll"
    WASTE_GENERAL_KEYWORDS: list[str] = ["müll", "muell", "abfall", "tonne"]

    # Signal settings
    SIGNAL_PHONE_NUMBER: str = os.getenv("SIGNAL_PHONE_NUMBER", "")
    SIGNAL_GROUP_ID: str = os.getenv("SIGNAL_GROUP_ID", "")

    # Emergency Contact
    EMERGENCY_CONTACT_NAME: str = os.getenv("EMERGENCY_CONTACT_NAME", "Notfall-Kontakt")
    EMERGENCY_CONTACT_NUMBER: str = os.getenv("EMERGENCY_CONTACT_NUMBER", "Keine Nummer hinterlegt")