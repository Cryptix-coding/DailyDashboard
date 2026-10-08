from flask import Flask, render_template
from config import Config
from services.time_service import get_current_datetime
from services.weather_service import get_current_weather
from services.calendar_service import get_agenda_days
from services.waste_service import get_active_waste_alert
from services.medication_service import get_active_medication_alert
from services.signal_service import start_signal_listener, get_active_signal_message
from services.emergency_service import get_emergency_contacts

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/tile/time")
def tile_time():
    time_data = get_current_datetime()
    return render_template("partials/time_tile.html", data=time_data)


@app.route("/tile/weather")
def tile_weather():
    weather_data = get_current_weather()
    return render_template("partials/weather_tile.html", weather=weather_data)


@app.route("/tile/calendar")
def tile_calendar():
    agenda_data = get_agenda_days()
    return render_template("partials/calendar_tile.html", agenda=agenda_data)


@app.route("/tile/waste")
def tile_waste():
    waste_items = get_active_waste_alert()
    return render_template("partials/waste_tile.html", waste_items=waste_items)


@app.route("/tile/medication")
def tile_medication():
    med_data = get_active_medication_alert()
    return render_template("partials/medication_tile.html", med=med_data)


@app.route("/tile/signal")
def tile_signal():
    signal_data = get_active_signal_message()
    return render_template("partials/signal_tile.html", signal=signal_data)


@app.route("/tile/emergency")
def tile_emergency():
    contacts_data = get_emergency_contacts()
    return render_template("partials/emergency_tile.html", contacts=contacts_data)


if __name__ == "__main__":
    start_signal_listener()
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=Config.PORT)