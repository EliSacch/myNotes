import hmac
import re
import secrets


from flask import Blueprint, redirect, render_template, request, session, url_for, flash
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager, limiter
from app.models import Dashboard, User

auth_bp = Blueprint("auth", __name__)

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
COMMON_PASSWORDS = {"password", "password123", "qwerty", "letmein", "12345678"}


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


def _register_context(errors=None, username="", email=""):
    csrf_token = session.get("register_csrf_token")
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        session["register_csrf_token"] = csrf_token

    return {
        "action": url_for("auth.register"),
        "csrf_token": csrf_token,
        "email": email,
        "errors": errors or [],
        "title": "Create your account",
        "username": username,
    }

def _login_context(errors=None, email=""):
    csrf_token = session.get("login_csrf_token")
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        session["login_csrf_token"] = csrf_token

    return {
        "action": url_for("auth.login"),
        "csrf_token": csrf_token,
        "email": email,
        "errors": errors or [],
        "title": "Login to your account",
    }

@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute; 10 per hour", methods=["POST"])
def register():
    errors = {
        "form": [],
        "username": [],
        "email": [],
        "password": [],
        "confirm_password": [],
    }
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        submitted_token = request.form.get("csrf_token", "")
        stored_token = session.get("register_csrf_token", "")
        if not (
            isinstance(submitted_token, str)
            and isinstance(stored_token, str)
            and hmac.compare_digest(submitted_token, stored_token)
        ):
            errors["form"].append("Your form has expired. Please try again.")

        if not 3 <= len(username) <= 50:
            errors["username"].append("Username must be between 3 and 50 characters.")
        elif not USERNAME_PATTERN.fullmatch(username):
            errors["username"].append("Username may contain only letters, numbers, and underscores.")

        if len(email) > 100 or not EMAIL_PATTERN.fullmatch(email):
            errors["email"].append("Enter a valid email address.")

        if not 12 <= len(password) <= 128:
            errors["password"].append("Password must be between 12 and 128 characters.")
        if password != confirm_password:
            errors["confirm_password"].append("Passwords do not match.")
        if password.casefold() in COMMON_PASSWORDS:
            errors["password"].append("Choose a less common password.")
        if password and not any(character.islower() for character in password):
            errors["password"].append("Password must include a lowercase letter.")
        if password and not any(character.isupper() for character in password):
            errors["password"].append("Password must include an uppercase letter.")
        if password and not any(character.isdigit() for character in password):
            errors["password"].append("Password must include a number.")
        if password and not any(not character.isalnum() for character in password):
            errors["password"].append("Password must include a symbol.")
        if username and username.casefold() in password.casefold():
            errors["password"].append("Password must not contain your username.")
        email_local_part = email.partition("@")[0]
        if email_local_part and email_local_part.casefold() in password.casefold():
            errors["password"].append("Password must not contain your email address.")

        if not any(errors.values()):
            username_exists = db.session.scalar(
                db.select(User.id).where(func.lower(User.username) == username.lower())
            )
            email_exists = db.session.scalar(
                db.select(User.id).where(func.lower(User.email) == email)
            )
            if username_exists or email_exists:
                errors["form"].append("Unable to create an account with those details.")
                if username_exists:
                    errors["username"].append("Username already exists.")
                else:
                    errors["email"].append("Email already exists.")

        if any(errors.values()):
            return render_template(
                "auth/register.html",
                **_register_context(errors, username, email),
            )

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )
        new_user.dashboards.append(
            Dashboard(name="My Dashboard", is_default=True)
        )
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template(
                "auth/register.html",
                **_register_context(
                    errors={"form": "Unable to create an account with those details."},
                    username=username,
                    email=email,
                ),
            )

        session.pop("register_csrf_token", None)
        login_user(new_user)
        return redirect(url_for("index"))
    return render_template("auth/register.html", **_register_context())

@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("3 per minute; 10 per hour", methods=["POST"])
def login():
    errors = {
        "form": [],
        "email": [],
        "password": [],
    }
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        submitted_token = request.form.get("csrf_token", "")
        stored_token = session.get("login_csrf_token", "")
        if not (
            isinstance(submitted_token, str)
            and isinstance(stored_token, str)
            and hmac.compare_digest(submitted_token, stored_token)
        ):
            errors["form"].append("Your form has expired. Please try again.")
        if not email:
            errors["email"].append("Email is required.")
        if not password:
            errors["password"].append("Password is required.")
        if not EMAIL_PATTERN.fullmatch(email):
            errors["email"].append("Enter a valid email address.")
        if not any(errors.values()):
            user = db.session.scalar(
                db.select(User).where(func.lower(User.email) == email)
            )
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                flash(f"Welcome back, {user.username}!", "success")
                return redirect(url_for("index"))
            else:
                errors["form"].append("Invalid email or password.")
        if any(errors.values()):
            return render_template("auth/login.html", **_login_context(errors, email))
    return render_template("auth/login.html", **_login_context())
    
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))
