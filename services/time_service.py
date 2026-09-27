import datetime
from config import Config


def get_current_datetime() -> dict[str, str]:
    """Return the current date and time formatted for the German UI."""
    now = datetime.datetime.now()
    weekday = Config.WEEKDAYS[now.weekday()]
    month = Config.MONTHS[now.month]

    return {
        "date": f"{weekday}, {now.day}. {month} {now.year}",
        "time": now.strftime("%H:%M Uhr")
    }