from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)


# user model - refactor ?
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(75), nullable=False, unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# Create the database
with app.app_context():
    db.create_all()

@app.route("/")
def pre_home():
    """
    Landing page before logging in
    """
    return render_template("pre_home.html")


@app.route("/home") # update router to /home
def home():
    """
    Home Page router
    """
    if "user_id" in session:
        clients = get_clients() 
        return render_template(
            "users/home.html", username=session["username"], clients=clients
        )
    return redirect(url_for("pre_home"))
    # return render_template("pre_home.html")


@app.route("/register", methods=["GET", "POST"])
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
        return redirect(url_for("login"))
    return render_template("users/register.html")


@app.route("/login", methods=["GET", "POST"])
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
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials. Please try again.")
    return render_template("users/login.html")


@app.route("/update", methods=["GET", "POST"])
def update():
    """
    Update user info router
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    # this needs to change to populate the update form. 
    user = User.query.get(session["user_id"])
    print()
    print(user.first_name)
    print()

    if request.method == "POST":
        user.username = request.form["username"]
        user.first_name = request.form["first_name"]
        user.last_name = request.form["last_name"]
        user.email = request.form["email"]
        if request.form["password"]:
            user.password = generate_password_hash(request.form["password"])
        db.session.commit()
        flash("User details updated successfully.")
        return redirect(url_for("home"))

    return render_template("users/update.html", user=user)


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("pre_home"))


# -------------------------------------------------------------------------------
#  FastAPI - Client communication pipe
# -------------------------------------------------------------------------------


def get_clients():
    try:
        response = requests.get("http://127.0.0.1:8000/client/")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []

# update redirects from login to pre_home?
@app.route("/clients")
def clients():
    """
    Router for client home page
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    # clients = get_clients()
    return render_template("clients/clients.html")

@app.route("/clients/manage")
def manage_clients():
    """
    Router for manage client table
    """
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    clients = get_clients()
    return render_template("clients/manage_clients.html", clients=clients)

@app.route("/clients/roster")
def view_clients():
    """
    View Roster router
    """
    if "user_id" not in session:
        return redirect(url_for("login"))
    clients = get_clients()
    return render_template("clients/view_clients.html", clients=clients)


@app.route("/clients/new", methods=["GET", "POST"])
def create_client():
    """
    Post/Create Client Pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        client_data = {
            "name": request.form["name"],
            "email": request.form["email"],
            "address": request.form["address"],
            "city": request.form["city"],
            "state": request.form["state"],
            "date": request.form["date"],
        }

        response = requests.post("http://127.0.0.1:8000/client/", json=client_data)
        print()
        print(response)
        print()
        if response.status_code == 200:
            flash("Client created successfully.")
            return redirect(url_for("clients"))
        elif response.status_code == 400:
            flash(response.json()['detail'])
        else:
            flash("Failed to create client.")

    return render_template("clients/create_clients.html")


@app.route("/clients/edit/<int:client_id>", methods=["GET", "POST"])
def update_client(client_id):
    """
    Put/Update Client Pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        client_data = {
            "name": request.form["name"],
            "email": request.form["email"],
            "address": request.form["address"],
            "city": request.form["city"],
            "state": request.form["state"],
            "date": request.form["date"],
        }
        response = requests.put(
            f"http://127.0.0.1:8000/client/{client_id}", json=client_data
        )
        if response.status_code == 200:
            flash("Client updated successfully.")
            return redirect(url_for("clients"))
        else:
            flash("Failed to update client.")

    client = get_client(client_id)
    return render_template("clients/update_clients.html", client=client)


@app.route("/clients/delete/<int:client_id>", methods=["POST"])
def delete_client(client_id):
    """
    Delete Client pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("login"))
    # pop-up for IH2, IH7
    if request.form.get("confirm") == "yes":
        response = requests.delete(f"http://127.0.0.1:8000/client/{client_id}")
        if response.status_code == 200:
            flash("Client deleted successfully.")
        else:
            flash("Error: Failed to delete client.")
        return redirect(url_for("manage_clients"))
    else:
        flash("Delete operation cancelled.")
    return redirect(url_for("manage_clients"))


def get_client(client_id):
    try:
        response = requests.get(f"http://127.0.0.1:8000/client/{client_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


if __name__ == "__main__":
    app.run(debug=True)
