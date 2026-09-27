import datetime
import requests
import icalendar
import recurring_ical_events
from typing import Any, Optional
from config import Config


def get_agenda_days() -> Optional[list[dict[str, Any]]]:
    """
    Fetch appointments from the ICS calendar and group them into a 3-day agenda
    (Today, Tomorrow, Day after tomorrow).
    Returns None if the calendar URL is missing or the network request fails.
    """
    if not Config.CALENDAR_ICS_URL:
        print("[CalendarService] Warning: CALENDAR_ICS_URL is not set in .env")
        return None

    try:
        response = requests.get(Config.CALENDAR_ICS_URL, timeout=10)
        response.raise_for_status()
        calendar = icalendar.Calendar.from_ical(response.text)
    except Exception as error:
        print(f"[CalendarService] Error fetching calendar data: {error}")
        return None

    now = datetime.datetime.now().astimezone()
    today = now.date()

    # Define the 3 target days for the agenda
    day_labels = ["Heute", "Morgen", "Übermorgen"]
    agenda: dict[datetime.date, dict[str, Any]] = {}

    for offset, label in enumerate(day_labels):
        target_date = today + datetime.timedelta(days=offset)
        weekday_name = Config.WEEKDAYS[target_date.weekday()]
        agenda[target_date] = {
            "label": label,
            "date_str": f"{weekday_name}, {target_date.strftime('%d.%m.')}",
            "is_today": offset == 0,
            "events": []
        }

    # Query range: start of today until the end of the day after tomorrow (+3 days)
    query_end = today + datetime.timedelta(days=3)
    raw_events = recurring_ical_events.of(calendar).between(today, query_end)

    for event in raw_events:
        summary = str(event.get("SUMMARY", "Termin"))
        dtstart = event.get("DTSTART").dt

        # Distinguish between all-day events (date) and timed events (datetime)
        if isinstance(dtstart, datetime.datetime):
            local_dt = dtstart.astimezone() if dtstart.tzinfo else dtstart
            event_date = local_dt.date()
            time_str = local_dt.strftime("%H:%M Uhr")
            sort_key = local_dt.strftime("%H:%M")
        else:
            event_date = dtstart
            time_str = "Ganztägig"
            sort_key = "00:00"

        if event_date in agenda:
            agenda[event_date]["events"].append({
                "sort_key": sort_key,
                "time": time_str,
                "title": summary
            })

    # Sort events chronologically within each day
    for day_data in agenda.values():
        day_data["events"].sort(key=lambda item: item["sort_key"])

    return list(agenda.values())