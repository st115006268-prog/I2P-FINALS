"""Arcadia sign-in page, served with Flask.

Run:
    python -m pip install flask
    python app.py
Then open http://127.0.0.1:5000
"""
import re
import secrets

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # demo only; use a fixed secret from config in production

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
MIN_PASSWORD_LENGTH = 6

FEATURES = [
    ("01", "Plan with clarity", "Keep tasks and study sessions in one place."),
    ("02", "Practice actively", "Turn your material into decks and quizzes."),
    ("03", "Stay consistent", "Build routines with focused timers and goals."),
]


def validate(email: str, password: str) -> dict:
    errors = {}
    if not EMAIL_RE.match(email):
        errors["email"] = "Please enter a valid email address."
    if len(password) < MIN_PASSWORD_LENGTH:
        errors["password"] = f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    return errors


@app.route("/", methods=["GET", "POST"])
def login():
    errors, email, remember = {}, "", True

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"
        errors = validate(email, password)

        if not errors:
            # Design preview: any valid email + 6-char password signs in.
            session["user"] = email
            session.permanent = remember
            return redirect(url_for("login"))

    return render_template(
        "login.html",
        features=FEATURES,
        errors=errors,
        email=email,
        remember=remember,
        user=session.get("user"),
    )


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
