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

bp = Blueprint("library", __name__)


@bp.route("/")
def index():
    """
    Library home page
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    return render_template("library/library.html")


@bp.route("/view")
def view_library():
    """
    Router for view library table
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    library = get_piece_all()
    return render_template("library/view_library.html", pieces=library)


# ----------------------------------------------------------------------------------
#   Library microservice routers
# ----------------------------------------------------------------------------------


@bp.route("/add", methods=["GET", "POST"])
def add_piece():
    """
    Post/Create Piece Pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    if request.method == "POST":
        piece_data = {
            "title": request.form["title"],
            "composer": request.form["composer"],
            "instrumentation": request.form["instrumentation"],
            "duration": request.form["duration"],
        }

        response = requests.post("http://127.0.0.1:8127/library/", json=piece_data)
        if response.status_code == 200:
            flash(f"{request.form['title']} successfully added.", "success")
            return redirect(url_for("library.view_library"))
        elif response.status_code == 400:
            flash(response.json()["detail"], "error")
        else:
            flash("Failed to add piece.", "error")

    return render_template("library/add_piece.html")


@bp.route("/edit/<int:piece_id>", methods=["GET", "POST"])
def update_piece(piece_id):
    """
    Put/Update Piece Pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    if request.method == "POST":
        piece_data = {
            "title": request.form["title"],
            "composer": request.form["composer"],
            "instrumentation": request.form["instrumentation"],
            "duration": request.form["duration"],
        }

        response = requests.put(
            f"http://127.0.0.1:8127/library/{piece_id}", json=piece_data
        )
        if response.status_code == 200:
            flash("Piece updated successfully.", "success")
            return redirect(url_for("library.view_library"))

        elif response.status_code == 400:
            flash(response.json()["detail"], "error")
        else:
            flash("Failed to update piece.", "error")

    piece = get_piece_id(piece_id)

    return render_template("library/edit_piece.html", piece=piece)


@bp.route("/delete/<int:piece_id>", methods=["POST"])
def delete_piece(piece_id):
    """
    Delete Piece pipeline
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))

    if request.method == "POST":
        response = requests.delete(f"http://127.0.0.1:8127/library/{piece_id}")
        if response.status_code == 200:
            flash("Piece deleted successfully.", "success")
        else:
            flash("Error: Failed to delete piece.", "error")
        return redirect(url_for("library.view_library"))
    else:
        flash("Delete operation cancelled.", "warning")
    return redirect(url_for("library.view_library"))


@bp.route("/generate/", methods=["GET", "POST"])
def generate():
    """
    Returns a set list of pieces generated by the server
    """
    if "user_id" not in session:
        return redirect(url_for("index.login"))
    if request.method == "GET":
        set_list = generate_random_setlist()
        return render_template("library/set_list.html", pieces=set_list)
    return render_template("library/set_list.html", pieces=None)


# ----------------------------------------------------------------------------------
#   Utilities
# ----------------------------------------------------------------------------------


def get_piece_all():
    """
    return all pieces from the DB
    """
    try:
        response = requests.get("http://127.0.0.1:8127/library/")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return []


def get_piece_id(piece_id):
    """
    return piece by id from DB
    """
    try:
        response = requests.get(f"http://127.0.0.1:8127/library/{piece_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def generate_random_setlist():
    """
    return random set of 10 pieces from DB
    """
    try:
        response = requests.get(f"http://127.0.0.1:8127/library/generate/")
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None
