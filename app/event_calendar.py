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
from models import User, db
import requests, os
from datetime import datetime, timedelta

bp = Blueprint("event_calendar", __name__)

@bp.route("/")
def index():
    """
    Calendar Home Page
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))
    
    today = datetime.today()
    year, month = today.year, today.month
    
    return redirect(url_for("event_calendar.view_calendar", year=year, month=month))

@bp.route("/<int:year>/<int:month>")
def view_calendar(year,month):
    """
    display calendar with events
    """

    first_day = datetime(year, month, 1)
    days_in_month = (datetime(year, month + 1, 1) - timedelta(days=1)).day if month != 12 else 31
    start_weekday = first_day.weekday()
    # get events
    events = {}
    return render_template("calendar/view_calendar.html", year=year, month=month, days_in_month=days_in_month, start_weekday=start_weekday, events=events)

@bp.route("/add", methods=["GET", "POST"])
def add_event():
    """
    Post/Create Event Pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    if request.method == "POST":
        event_data = {
            "date": request.form["date"],
            "client": request.form["client"],
            "location": request.form["location"],
            "duration": request.form["duration"],
        }

        #  CHANGE THIS!!!!!!! PORT TOO
        response = requests.post("http://127.0.0.1:8327/library/", json=event_data)
        print()
        print(response)
        print()
        if response.status_code == 200:
            flash(f"Event successfully added.")
            return redirect(url_for("event_calendar.index"))
        elif response.status_code == 400:
            flash(response.json()["detail"])
        else:
            flash("Failed to add event.")

    return render_template("calendar/add_event.html")


