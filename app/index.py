from flask import (
    render_template,
    redirect,
    url_for,
    request,
    session,
    flash,
    Blueprint,
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db

bp = Blueprint("index", __name__)


@bp.route("/")
def home():
    """
    Landing page before logging in
    """
    return render_template("pre_home.html")


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
            flash("Invalid credentials. Please try again.", "warning")
    return render_template("users/login.html")


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
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("index.login"))
    return render_template("users/register.html")
