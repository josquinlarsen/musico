from flask import (
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    Blueprint,
)
import requests
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
    """
    returns the next or previous month to toggle calendar view
    """

    update_year, update_month = date_modulo(year, month)
    return view_calendar(update_year, update_month)


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
            "event_type": request.form["event_type"],
            "location": request.form["location"],
            "duration": request.form["duration"],
            "notes": request.form["notes"],
        }

        response = requests.post("http://127.0.0.1:8327/calendar/", json=event_data)
        if response.status_code == 200:
            flash(f"Event successfully added.", "success")
            return redirect(url_for("event_calendar.index"))
        elif response.status_code == 400:
            flash(response.json()["detail"], "error")
        else:
            flash("Failed to add event.", "error")

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
            "event_type": request.form["event_type"],
            "location": request.form["location"],
            "duration": request.form["duration"],
            "notes": request.form["notes"],
        }

        response = requests.put(
            f"http://127.0.0.1:8327/calendar/{event_id}", json=event_data
        )
        if response.status_code == 200:
            flash("Event updated successfully.", "success")
            return redirect(url_for("event_calendar.index"))

        elif response.status_code == 400:
            flash(response.json()["detail"], "error")
        else:
            flash("Failed to update event.", "error")

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
            flash("Event deleted successfully.", "success")
        else:
            flash("Error: Failed to delete event.", "error")
        return redirect(url_for("event_calendar.view_calendar"))
    else:
        flash("Delete operation cancelled.", "warning")
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


def date_modulo(year, month):
    """
    returns month, accounts for wrap around
    """
    if month > 12:
        return (year + 1), 1
    if month < 1:
        return (year - 1), 12
    return year, month
