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
import requests, os, json
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
    events = get_event_all()
    return redirect(
        url_for("event_calendar.view_calendar", year=year, month=month, events=events)
    )


@bp.route("/<int:year>/<int:month>")
def view_calendar(year, month):
    """
    display calendar with events
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))
    first_day = datetime(year, month, 1)
    days_in_month = (
        (datetime(year, month + 1, 1) - timedelta(days=1)).day if month != 12 else 31
    )
    start_weekday = first_day.weekday()

    month_name = month_to_text(month)
    events = get_event_all()

    return render_template(
        "calendar/view_calendar.html",
        month_name=month_name,
        year=year,
        month=month,
        days_in_month=days_in_month,
        start_weekday=start_weekday,
        events=events,
    )


@bp.route("/change/<int:year>/<int:month>")
def change_month(year, month):

    update_year, update_month = month_modulo(year, month)
    print(update_year, update_month)
    return view_calendar(update_year, update_month)


@bp.route("/current/<int:year><int:month>")

# ----------------------------------------------------------------------------------
#   Calendar microservice routers
# ----------------------------------------------------------------------------------


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
            "event_name": request.form["event_name"],
            "location": request.form["location"],
            "duration": request.form["duration"],
            "notes": request.form["notes"],
        }

        response = requests.post("http://127.0.0.1:8327/calendar/", json=event_data)
        if response.status_code == 200:
            flash(f"Event successfully added.")
            return redirect(url_for("event_calendar.index"))
        elif response.status_code == 400:
            flash(response.json()["detail"])
        else:
            flash("Failed to add event.")

    return render_template("calendar/add_event.html")


@bp.route("/edit/<int:event_id>", methods=["GET", "POST"])
def update_event(event_id):
    """
    Put/Update Event Pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    if request.method == "POST":
        event_data = {
            "date": request.form["date"],
            "event_name": request.form["event_name"],
            "location": request.form["location"],
            "duration": request.form["duration"],
            "notes": request.form["notes"],
        }

        response = requests.put(
            f"http://127.0.0.1:8327/calendar/{event_id}", json=event_data
        )
        if response.status_code == 200:
            flash("Event updated successfully.")
            return redirect(url_for("event_calendar.index"))

        elif response.status_code == 400:
            flash(response.json()["detail"])
        else:
            flash("Failed to update event.")

    event = get_event_id(event_id)

    return render_template("calendar/edit_event.html", event=event)


@bp.route("/delete/<int:event_id>", methods=["POST"])
def delete_event(event_id):
    """
    Delete Event pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    if request.method == "POST":
        response = requests.delete(f"http://127.0.0.1:8327/calendar/{event_id}")
        if response.status_code == 200:
            flash("Event deleted successfully.")
        else:
            flash("Error: Failed to delete event.")
        return redirect(url_for("event_calendar.view_calendar"))
    else:
        flash("Delete operation cancelled.")
    return redirect(url_for("event_calendar.view_calendar"))


@bp.route("/detail/<int:event_id>", methods=["GET", "POST"])
def event_detail(event_id):
    """
    Event detail router for update/delete
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    event = get_event_id(event_id)
    return render_template("calendar/event_detail.html", event=event)


# ----------------------------------------------------------------------------------
#   Utilities
# ----------------------------------------------------------------------------------


def get_event_all():
    """
    return all events from the DB
    """
    try:
        response = requests.get("http://127.0.0.1:8327/calendar/")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []


def get_event_id(event_id):
    """
    return event by id from DB
    """
    try:
        response = requests.get(f"http://127.0.0.1:8327/calendar/{event_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def month_to_text(month):
    """
    Convert month number to text for display
    """
    month_dico = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    return month_dico[month]


def month_modulo(year, month):
    """
    returns month and accounts for wrap around
    """
    if month > 12:
        return (year + 1), 1
    if month < 1:
        return (year - 1), 12
    return year, month
