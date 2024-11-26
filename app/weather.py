from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    Blueprint,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
import requests, json

bp = Blueprint("weather", __name__)


@bp.route("/", methods=["GET", "POST"])
def index():
    """
    Weather home page
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    if request.method == "POST":

        zipcode = request.form["zipcode"]
        response = requests.get(f"http://127.0.0.1:8227/weather/{zipcode}")

        weather_data = format_json(response.json())

        if response.status_code == 200:
            return render_template("weather/display_weather.html", zipcode=zipcode, weather=weather_data)
        elif response.status_code == 400:
            flash(response.json()["detail"])
        else:
            flash("Failed to get weather.")

    return render_template("weather/get_weather.html")


def format_json(weather_json):
    """
    Format json for display
    """
    weather_data = []
    weather_data.append(weather_json["temperature"])
    for item in weather_json["messages"]:
        weather_data.append(item["message"])

    return weather_data


def get_current_weather(zipcode: str):
    """
    Takes zipcode and returns microservice weather data
    """

    try:
        response = requests.get(f"http://127.0.0.1:8227/weather/{zipcode}")
        response.raise_for_status()
        weather = response.json()
        return weather
    except requests.RequestException:
        return None
