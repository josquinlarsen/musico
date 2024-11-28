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
from models import db
import datetime 
import clients, event_calendar, index, library, users, weather


app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db.init_app(app)

@app.template_filter("format_date")
def format_date(date_value):
    """
    Convert Date to more USA freindly format
    """
    month_dico = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Sept",
        "10": "Oct",
        "11": "Nov",
        "12": "Dec",
    }
    date_array = date_value.split('-')
    formatted_date = f"{date_array[2]} {month_dico[date_array[1]]} {date_array[0]}"

    return formatted_date

# register Blueprints
app.register_blueprint(index.bp)
app.register_blueprint(clients.bp, url_prefix="/clients")
app.register_blueprint(users.bp, url_prefix="/users")
app.register_blueprint(library.bp, url_prefix="/library")
app.register_blueprint(weather.bp, url_prefix="/weather")
app.register_blueprint(event_calendar.bp, url_prefix="/event_calendar")

# Create the database
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
