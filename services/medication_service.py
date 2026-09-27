import datetime
from typing import Any, Optional


# Time slots (top to bottom rows on the blister)
MEDICATION_SLOTS = [
    {
        "id": "nuechtern",
        "label": "Nüchtern",
        "start": (6, 30),
        "end": (8, 0),
        "theme": "red"
    },
    {
        "id": "morgens",
        "label": "Morgens",
        "start": (8, 0),
        "end": (9, 30),
        "theme": "green"
    },
    {
        "id": "mittags",
        "label": "Mittags",
        "start": (11, 30),
        "end": (13, 0),
        "theme": "pink"
    },
    {
        "id": "abends",
        "label": "Abends",
        "start": (19, 30),
        "end": (21, 30),
        "theme": "orange"
    },
]

# Visual column order from LEFT to RIGHT
# (Blister starts on the RIGHT with Tuesday/Di and progresses LEFT to Monday/Mo)
BLISTER_COLUMNS = [
    {"weekday": 0, "short": "Mo", "chrono_idx": 6},
    {"weekday": 6, "short": "So", "chrono_idx": 5},
    {"weekday": 5, "short": "Sa", "chrono_idx": 4},
    {"weekday": 4, "short": "Fr", "chrono_idx": 3},
    {"weekday": 3, "short": "Do", "chrono_idx": 2},
    {"weekday": 2, "short": "Mi", "chrono_idx": 1},
    {"weekday": 1, "short": "Di", "chrono_idx": 0},
]


def get_active_medication_alert() -> Optional[dict[str, Any]]:
    """
    Check if the current time falls into one of the 4 medication windows.
    If active, return the complete 4x7 blister grid state; otherwise return None.
    """
    now = datetime.datetime.now().astimezone()
    current_minutes = now.hour * 60 + now.minute

    active_row_idx: Optional[int] = None
    active_slot: Optional[dict[str, Any]] = None

    for idx, slot in enumerate(MEDICATION_SLOTS):
        start_min = slot["start"][0] * 60 + slot["start"][1]
        end_min = slot["end"][0] * 60 + slot["end"][1]
        if start_min <= current_minutes < end_min:
            active_row_idx = idx
            active_slot = slot
            break

    # Outside the medication time windows -> hide the box
    if active_slot is None or active_row_idx is None:
        return None

    today_weekday = now.weekday()
    today_chrono_idx = next(
        col["chrono_idx"] for col in BLISTER_COLUMNS if col["weekday"] == today_weekday
    )

    # Build the 4 rows x 7 columns blister matrix
    rows = []
    for row_idx, slot in enumerate(MEDICATION_SLOTS):
        cells = []
        for col in BLISTER_COLUMNS:
            col_chrono = col["chrono_idx"]

            # Compare chronological position in the blister week (Tuesday 0 -> Monday 6)
            if (col_chrono, row_idx) < (today_chrono_idx, active_row_idx):
                state = "taken"   # Already taken -> X
            elif (col_chrono, row_idx) == (today_chrono_idx, active_row_idx):
                state = "active"  # Take right now -> Colored circle
            else:
                state = "future"  # Still closed -> Empty box

            cells.append({
                "day_short": col["short"],
                "is_today": col["weekday"] == today_weekday,
                "state": state
            })

        rows.append({
            "label": slot["label"],
            "theme": slot["theme"],
            "is_active_row": row_idx == active_row_idx,
            "cells": cells
        })

    return {
        "slot_label": active_slot["label"],
        "theme": active_slot["theme"],
        "columns": [
            {"short": col["short"], "is_today": col["weekday"] == today_weekday}
            for col in BLISTER_COLUMNS
        ],
        "rows": rows
    }