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
import requests

bp = Blueprint("clients", __name__)


@bp.route("/")
def clients():
    """
    Router for client home page
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))
    # clients = get_clients()
    return render_template("clients/clients.html")


@bp.route("/manage")
def manage_clients():
    """
    Router for manage client table
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    clients = get_clients()
    return render_template("clients/manage_clients.html", clients=clients)


@bp.route("/sort/<direction>", methods=["GET", "POST"])
def sort_dates(direction):
    """
    Router to get sorted clients by date from microservice
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    sorted_clients = sort_by_date(direction)
    return render_template("clients/manage_clients.html", clients=sorted_clients)


@bp.route("/roster")
def view_clients():
    """
    View Roster router
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))
    clients = get_clients()
    return render_template("clients/view_clients.html", clients=clients)


@bp.route("/new", methods=["GET", "POST"])
def create_client():
    """
    Post/Create Client Pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

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
            return redirect(url_for("clients.manage_clients"))
        elif response.status_code == 400:
            flash(response.json()["detail"])
        else:
            flash("Failed to create client.")

    return render_template("clients/create_clients.html")


@bp.route("/edit/<int:client_id>", methods=["GET", "POST"])
def update_client(client_id):
    """
    Put/Update Client Pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

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
            return redirect(url_for("clients.manage_clients"))

        elif response.status_code == 400:
            flash(response.json()["detail"])
        else:
            flash("Failed to update client.")

    client = get_client(client_id)
    return render_template("clients/update_clients.html", client=client)


@bp.route("/delete/<int:client_id>", methods=["POST"])
def delete_client(client_id):
    """
    Delete Client pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))
    # pop-up for IH2, IH7
    if request.form.get("confirm") == "yes":
        response = requests.delete(f"http://127.0.0.1:8000/client/{client_id}")
        if response.status_code == 200:
            flash("Client deleted successfully.")
        else:
            flash("Error: Failed to delete client.")
        return redirect(url_for("clients.manage_clients"))
    else:
        flash("Delete operation cancelled.")
    return redirect(url_for("clients.manage_clients"))


def get_clients():
    try:
        response = requests.get("http://127.0.0.1:8000/client/")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []


def get_client(client_id):
    try:
        response = requests.get(f"http://127.0.0.1:8000/client/{client_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def sort_by_date(direction):
    try:
        response = requests.get(f"http://127.0.0.1:8000/client/{direction}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

