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
from models.user import User, db
import requests

import clients, users, index


app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db.init_app(app)

# register Blueprints
app.register_blueprint(index.bp)
app.register_blueprint(clients.bp, url_prefix="/clients")
app.register_blueprint(users.bp, url_prefix="/users")

# Create the database
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
