from flask import Flask, render_template, redirect, url_for, request, session, flash, Blueprint
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User, db
import requests

from clients import get_clients, get_client

bp = Blueprint("users", __name__)

# @bp.route("/")
# def pre_home():
#     """
#     Landing page before logging in
#     """
#     return render_template("pre_home.html")


@bp.route("/home") # update router to /home
def home():
    """
    Home Page router
    """
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        clients = get_clients() 
        return render_template(
            "users/home.html", username=session["username"], user=user, clients=clients
        )
    return redirect(url_for("index.home"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Register User Router
    """
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=hashed_password,
        )

        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("users.login"))
    return render_template("users/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """
    User Login Router
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("users.home"))
        else:
            flash("Invalid credentials. Please try again.")
    return render_template("users/login.html")

@bp.route("/profile")
def profile():
    """
    Router to User's profile page
    """
    if "user_id" not in session:
        return redirect(url_for("index.home"))
    user = User.query.get(session["user_id"])
    return render_template(
            "users/profile.html", user=user
        )
    


@bp.route("/update", methods=["GET", "POST"])
def update():
    """
    Update user info router
    """
    if "user_id" not in session:
        return redirect(url_for("users.login"))

    user = User.query.get(session["user_id"])


    if request.method == "POST":
        user.username = request.form["username"]
        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.email = request.form["email"]

        if request.form["password"]:
            user.password = generate_password_hash(request.form["password"])
        db.session.commit()
        flash("User details updated successfully.")
        return redirect(url_for("users.home"))

    return render_template("users/update.html", user=user)


@bp.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("index.home"))

