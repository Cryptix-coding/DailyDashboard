import datetime
import requests
import icalendar
import recurring_ical_events
from typing import Any, Optional
from config import Config


def get_agenda_days() -> Optional[list[dict[str, Any]]]:
    """
    Fetch appointments from the ICS calendar and group them into a 5-day agenda.
    Multi-day events are displayed on every day they are active.
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

    # Define the 5 target days for the agenda
    relative_labels = ["Heute", "Morgen", "Übermorgen"]
    agenda: dict[datetime.date, dict[str, Any]] = {}

    for offset in range(5):
        target_date = today + datetime.timedelta(days=offset)
        weekday_name = Config.WEEKDAYS[target_date.weekday()]

        if offset < len(relative_labels):
            label = relative_labels[offset]
            date_str = f"{weekday_name}, {target_date.strftime('%d.%m.')}"
        else:
            # 4th and 5th day use the weekday name directly as the main label
            label = weekday_name
            date_str = target_date.strftime("%d.%m.")

        agenda[target_date] = {
            "label": label,
            "date_str": date_str,
            "is_today": offset == 0,
            "events": []
        }

    # Query range: start of today until the end of the 5th day (+5 days)
    query_end = today + datetime.timedelta(days=5)
    raw_events = recurring_ical_events.of(calendar).between(today, query_end)

    for event in raw_events:
        summary = str(event.get("SUMMARY", "Termin"))
        dtstart = event.get("DTSTART").dt
        dtend_prop = event.get("DTEND")
        dtend = dtend_prop.dt if dtend_prop else None

        # Distinguish between timed events (datetime) and all-day events (date)
        if isinstance(dtstart, datetime.datetime):
            local_start = dtstart.astimezone() if dtstart.tzinfo else dtstart
            start_date = local_start.date()
            time_str = local_start.strftime("%H:%M Uhr")
            sort_key = local_start.strftime("%H:%M")

            if dtend and isinstance(dtend, datetime.datetime):
                local_end = dtend.astimezone() if dtend.tzinfo else dtend
                # If a timed event ends exactly at 00:00, it doesn't count for the next day
                if local_end.time() == datetime.time.min and local_end.date() > start_date:
                    end_date = local_end.date() - datetime.timedelta(days=1)
                else:
                    end_date = local_end.date()
            else:
                end_date = start_date
        else:
            start_date = dtstart
            time_str = "Ganztägig"
            sort_key = "00:00"

            # In ICS standard, DTEND for all-day events is exclusive ( points to the day AFTER the last day)
            if dtend and not isinstance(dtend, datetime.datetime):
                end_date = dtend - datetime.timedelta(days=1)
                if end_date < start_date:
                    end_date = start_date
            else:
                end_date = start_date

        # Add the event to every day in our 5-day agenda between start_date and end_date
        current_date = max(start_date, today)
        last_agenda_date = today + datetime.timedelta(days=4)
        final_date = min(end_date, last_agenda_date)

        while current_date <= final_date:
            if current_date in agenda:
                # If a timed event spans multiple days, show "Ganztägig" on subsequent days
                display_time = time_str if current_date == start_date else "Ganztägig"
                display_sort = sort_key if current_date == start_date else "00:00"

                agenda[current_date]["events"].append({
                    "sort_key": display_sort,
                    "time": display_time,
                    "title": summary
                })
            current_date += datetime.timedelta(days=1)

    # Sort events chronologically within each day
    for day_data in agenda.values():
        day_data["events"].sort(key=lambda item: item["sort_key"])

    return list(agenda.values())