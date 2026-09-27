import datetime
import requests
import icalendar
import recurring_ical_events
from config import Config


def get_active_waste_alert() -> list[str]:
    """
    Check if a waste collection alert should be displayed right now.
    Rule:
      - From 17:00 on the day BEFORE collection -> check tomorrow's events
      - Until 09:00 on the day OF collection    -> check today's events
      - Between 09:00 and 17:00                 -> return empty list (hide box)
    """
    if not Config.CALENDAR_ICS_URL:
        return []

    now = datetime.datetime.now().astimezone()
    today = now.date()

    # Determine which date to check based on the 17:00 to 09:00 rule
    if now.hour < 9:
        target_date = today
    elif now.hour >= 17:
        target_date = today + datetime.timedelta(days=1)
    else:
        # Between 09:00 and 16:59 no alert is active
        return []

    try:
        response = requests.get(Config.CALENDAR_ICS_URL, timeout=10)
        response.raise_for_status()
        calendar = icalendar.Calendar.from_ical(response.text)
    except Exception as error:
        print(f"[WasteService] Error fetching calendar data: {error}")
        return []

    # Fetch events for the target date
    next_day = target_date + datetime.timedelta(days=1)
    raw_events = recurring_ical_events.of(calendar).between(target_date, next_day)

    detected_waste: list[str] = []

    for event in raw_events:
        dtstart = event.get("DTSTART").dt
        event_date = dtstart.astimezone().date() if isinstance(dtstart, datetime.datetime) else dtstart

        if event_date != target_date:
            continue

        summary = str(event.get("SUMMARY", ""))
        summary_lower = summary.lower()
        matched_specific = False

        # Check against specific waste types (Restmüll, Bio, Papier, Gelber Sack, Glas)
        for display_text, keywords in Config.WASTE_TYPES:
            if any(keyword in summary_lower for keyword in keywords):
                matched_specific = True
                if display_text not in detected_waste:
                    detected_waste.append(display_text)

        # Fallback: if it says "Müll" (e.g. "Sperrmüll") but didn't match the 5 standard types
        if not matched_specific:
            if any(keyword in summary_lower for keyword in Config.WASTE_GENERAL_KEYWORDS):
                fallback_text = f"🗑️ {summary}"
                if fallback_text not in detected_waste:
                    detected_waste.append(fallback_text)

    return detected_waste