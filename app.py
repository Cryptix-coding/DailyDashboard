from flask import Flask, render_template
from config import Config
from services.time_service import get_current_datetime
from services.weather_service import get_current_weather
from services.calendar_service import get_agenda_days
from services.waste_service import get_active_waste_alert
from services.medication_service import get_active_medication_alert

app = Flask(__name__)


@app.route("/")
def index():
    """Render the main dashboard layout."""
    return render_template("index.html")


@app.route("/tile/time")
def tile_time():
    """HTMX endpoint to update the date and time tile."""
    time_data = get_current_datetime()
    return render_template("partials/time_tile.html", data=time_data)


@app.route("/tile/weather")
def tile_weather():
    """HTMX endpoint to update the weather tile."""
    weather_data = get_current_weather()
    return render_template("partials/weather_tile.html", weather=weather_data)


@app.route("/tile/calendar")
def tile_calendar():
    """HTMX endpoint to update the 5-day calendar agenda tile."""
    agenda_data = get_agenda_days()
    return render_template("partials/calendar_tile.html", agenda=agenda_data)


@app.route("/tile/waste")
def tile_waste():
    """HTMX endpoint to display the waste alert (active 17:00 day before until 09:00 collection day)."""
    waste_items = get_active_waste_alert()
    return render_template("partials/waste_tile.html", waste_items=waste_items)


@app.route("/tile/medication")
def tile_medication():
    """HTMX endpoint to display the medication blister during intake windows."""
    med_data = get_active_medication_alert()
    return render_template("partials/medication_tile.html", med=med_data)


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=Config.PORT)