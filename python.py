from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)


# =========================
# OPEN HTML PAGE
# =========================

@app.route("/")
def home():

    return render_template("indexs.html")


# =========================
# CURRENT LOCATION RAIN
# =========================

@app.route("/rain")
def rain():

    try:

        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))

        url = "https://api.open-meteo.com/v1/forecast"

        params = {

            "latitude": lat,

            "longitude": lon,

            "current":
                "rain,precipitation,cloud_cover",

            "hourly":
                "rain,precipitation,"
                "precipitation_probability,"
                "cloud_cover",

            "forecast_days": 1,

            "timezone": "auto"
        }

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        current = data["current"]

        hourly = data["hourly"]

        rain_value = float(
            current.get("rain", 0) or 0
        )

        current_data = {

            "rain_now":
                rain_value > 0,

            "time":
                current.get("time"),

            "rain_mm":
                rain_value,

            "precipitation_mm":
                current.get(
                    "precipitation",
                    0
                ),

            "cloud_cover":
                current.get(
                    "cloud_cover",
                    0
                )
        }

        current_time = current.get("time")

        current_index = 0

        for i, time in enumerate(
            hourly["time"]
        ):

            if time == current_time:

                current_index = i

                break

        forecast = []

        for i in range(
            current_index + 1,
            min(
                current_index + 7,
                len(hourly["time"])
            )
        ):

            forecast.append({

                "time":
                    hourly["time"][i],

                "rain_mm":
                    hourly["rain"][i],

                "precipitation_mm":
                    hourly["precipitation"][i],

                "probability":
                    hourly[
                        "precipitation_probability"
                    ][i],

                "cloud_cover":
                    hourly["cloud_cover"][i]
            })

        return jsonify({

            "success": True,

            "current":
                current_data,

            "forecast":
                forecast
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


# =========================
# RAIN ACROSS INDIA
# =========================

@app.route("/india-rain")
def india_rain():

    try:

        latitudes = [

            8, 10, 12, 14, 16, 18, 20,
            22, 24, 26, 28, 30, 32, 34

        ]

        longitudes = [

            68, 70, 72, 74, 76, 78, 80,
            82, 84, 86, 88, 90, 92, 94

        ]

        locations = []

        for lat in latitudes:

            for lon in longitudes:

                locations.append(
                    (lat, lon)
                )

        latitude_string = ",".join(

            str(x[0])
            for x in locations

        )

        longitude_string = ",".join(

            str(x[1])
            for x in locations

        )

        url = (
            "https://api.open-meteo.com/"
            "v1/forecast"
        )

        params = {

            "latitude":
                latitude_string,

            "longitude":
                longitude_string,

            "current":
                "rain,precipitation",

            "timezone":
                "auto"
        }

        response = requests.get(

            url,

            params=params,

            timeout=60

        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):

            data = [data]

        rain_areas = []

        for location, weather in zip(
            locations,
            data
        ):

            current = weather.get(
                "current",
                {}
            )

            rain = float(
                current.get(
                    "rain",
                    0
                ) or 0
            )

            precipitation = float(
                current.get(
                    "precipitation",
                    0
                ) or 0
            )

            if (
                rain > 0
                or precipitation > 0
            ):

                rain_areas.append({

                    "lat":
                        location[0],

                    "lon":
                        location[1],

                    "rain_mm":
                        rain,

                    "precipitation_mm":
                        precipitation,

                    "radius":
                        90000
                })

        return jsonify({

            "success": True,

            "rain_areas":
                rain_areas
        })

    except Exception as e:

        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )