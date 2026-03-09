from flask import Flask, jsonify, request
from datetime import datetime
import pytz

app = Flask(__name__)

cities = {
    "Yerevan": {"tz": "Asia/Yerevan", "flag": "🇦🇲", "utc": "+4"},
    "Berlin": {"tz": "Europe/Berlin", "flag": "🇩🇪", "utc": "+1"},
    "Paris": {"tz": "Europe/Paris", "flag": "🇫🇷", "utc": "+1"},
    "New York": {"tz": "America/New_York", "flag": "🇺🇸", "utc": "-5"}
}

def day_or_night(hour):
    if 6 <= hour < 18:
        return "🌞"
    return "🌙"

@app.route("/time")
def get_time():
    selected_city = request.args.get("city")
    result = {}

    for city, data in cities.items():

        if selected_city and city != selected_city:
            continue

        tz = pytz.timezone(data["tz"])
        now = datetime.now(tz)

        result[city] = {
            "flag": data["flag"],
            "time": now.strftime("%H:%M:%S"),
            "icon": day_or_night(now.hour),
            "utc": data["utc"]
        }

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
