from flask import Flask, render_template
from config import Config
from services.time_service import get_current_datetime
from services.weather_service import get_current_weather

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


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=Config.PORT)