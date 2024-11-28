from flask import (
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    Blueprint,
)

from werkzeug.security import generate_password_hash
from models import User, db

from clients import get_clients

bp = Blueprint("users", __name__)


@bp.route("/home")
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


@bp.route("/profile")
def profile():
    """
    Router to User's profile page
    """
    if "user_id" not in session:
        return redirect(url_for("index.home"))
    user = User.query.get(session["user_id"])
    return render_template("users/profile.html", user=user)


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
