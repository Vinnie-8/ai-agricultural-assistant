import os
import uuid

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")


def login_required(view_func):
    """Redirects to /login if there's no access token in the session."""

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "access_token" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped


def auth_headers():
    token = session.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


@app.route("/")
def index():
    if "access_token" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/auth/register",
                json={
                    "full_name": full_name,
                    "email": email,
                    "password": password,
                },
                timeout=15,
            )
        except requests.RequestException:
            flash("Could not reach the backend. Is it running?", "danger")
            return render_template("register.html")

        if response.status_code == 201:
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))

        detail = response.json().get("detail", "Registration failed.")
        # detail can be a string (our own errors) or a list of Pydantic
        # validation error objects, depending on what failed.
        if isinstance(detail, list):
            detail = "; ".join(d.get("msg", "Invalid input") for d in detail)
        flash(detail, "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/auth/login",
                json={"email": email, "password": password},
                timeout=15,
            )
        except requests.RequestException:
            flash("Could not reach the backend. Is it running?", "danger")
            return render_template("login.html")

        if response.status_code == 200:
            data = response.json()
            session["access_token"] = data["access_token"]
            session["refresh_token"] = data["refresh_token"]
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))

        detail = response.json().get("detail", "Login failed.")
        flash(detail, "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        image = request.files.get("image")

        if not image or image.filename == "":
            flash("Please choose an image to upload.", "warning")
            return render_template("dashboard.html")

        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/diagnosis/predict",
                files={"image": (image.filename, image.stream, image.mimetype)},
                headers=auth_headers(),
                timeout=60,  # first request can be slow (model warm-up)
            )
        except requests.RequestException:
            flash("Could not reach the backend. Is it running?", "danger")
            return render_template("dashboard.html")

        if response.status_code != 201:
            detail = response.json().get("detail", "Diagnosis failed.")
            flash(str(detail), "danger")
            return render_template("dashboard.html")

        diagnosis = response.json()

        # Start a fresh chat session tied to this diagnosis.
        session["diagnosis"] = diagnosis
        session["chat_session_id"] = str(uuid.uuid4())
        session["chat_messages"] = []

        return redirect(url_for("diagnosis_result"))

    return render_template("dashboard.html")


@app.route("/diagnosis", methods=["GET"])
@login_required
def diagnosis_result():
    diagnosis = session.get("diagnosis")
    if not diagnosis:
        flash("No diagnosis yet — upload a photo first.", "info")
        return redirect(url_for("dashboard"))

    return render_template(
        "diagnosis.html",
        diagnosis=diagnosis,
        messages=session.get("chat_messages", []),
    )


@app.route("/diagnosis/chat", methods=["POST"])
@login_required
def diagnosis_chat():
    diagnosis = session.get("diagnosis")
    if not diagnosis:
        flash("No active diagnosis to chat about.", "info")
        return redirect(url_for("dashboard"))

    message = request.form.get("message", "").strip()
    if not message:
        return redirect(url_for("diagnosis_result"))

    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/chat",
            json={
                "message": message,
                "session_id": session["chat_session_id"],
                "diagnosis_id": diagnosis["id"],
                "location": request.remote_addr,
            },
            headers=auth_headers(),
            timeout=60,
        )
    except requests.RequestException:
        flash("Could not reach the backend. Is it running?", "danger")
        return redirect(url_for("diagnosis_result"))

    if response.status_code != 201:
        detail = response.json().get("detail", "Chat failed.")
        flash(str(detail), "danger")
        return redirect(url_for("diagnosis_result"))

    reply_data = response.json()

    messages = session.get("chat_messages", [])
    messages.append({"role": "user", "text": message})
    messages.append({"role": "assistant", "text": reply_data["reply"]})
    session["chat_messages"] = messages

    return redirect(url_for("diagnosis_result"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
