import hmac
import secrets
import smtplib

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.helpers.email import collect_email_errors
from app.helpers.username import collect_username_errors
from app.models import User
from app.routes.auth import resend_verification_csrf_token, send_verification_email

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")
_USERNAME_FORM_ERRORS_KEY = "username_form_errors"
_USERNAME_FORM_VALUES_KEY = "username_form_values"
_EMAIL_FORM_ERRORS_KEY = "email_form_errors"
_EMAIL_FORM_VALUES_KEY = "email_form_values"


def _profile_csrf_token():
    csrf_token = session.get("profile_csrf_token")
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        session["profile_csrf_token"] = csrf_token
    return csrf_token


def _has_valid_profile_csrf_token():
    submitted_token = request.form.get("csrf_token", "")
    stored_token = session.get("profile_csrf_token", "")
    return (
        isinstance(submitted_token, str)
        and isinstance(stored_token, str)
        and hmac.compare_digest(submitted_token, stored_token)
    )


def _redirect_to_profile():
    return redirect(url_for("profile.index"))


def _redirect_with_username_field_errors(errors, values):
    session[_USERNAME_FORM_ERRORS_KEY] = errors
    session[_USERNAME_FORM_VALUES_KEY] = values
    return _redirect_to_profile()


def _redirect_with_email_field_errors(errors, values):
    session[_EMAIL_FORM_ERRORS_KEY] = errors
    session[_EMAIL_FORM_VALUES_KEY] = values
    return _redirect_to_profile()


@profile_bp.route("/")
@login_required
def index():
    username_errors = session.pop(_USERNAME_FORM_ERRORS_KEY, {})
    username_values = session.pop(
        _USERNAME_FORM_VALUES_KEY,
        {"username": current_user.username},
    )
    email_errors = session.pop(_EMAIL_FORM_ERRORS_KEY, {})
    email_values = session.pop(
        _EMAIL_FORM_VALUES_KEY,
        {"email": current_user.email},
    )
    return render_template(
        "profile/index.html",
        user=current_user,
        csrf_token=resend_verification_csrf_token(),
        profile_csrf_token=_profile_csrf_token(),
        username_errors=username_errors,
        username_values=username_values,
        email_errors=email_errors,
        email_values=email_values,
    )


@profile_bp.route("/<int:user_id>/update-username", methods=["POST"])
@login_required
def update_username(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user != current_user:
        abort(403)

    username = (request.form.get("username") or "").strip()
    values = {"username": request.form.get("username", "")}

    if not _has_valid_profile_csrf_token():
        flash("Your form has expired. Please try again.", "warning")
        return _redirect_to_profile()

    field_errors = collect_username_errors(username)
    if not field_errors:
        username_taken = db.session.scalar(
            db.select(User.id).where(
                func.lower(User.username) == username.lower(),
                User.id != user.id,
            )
        )
        if username_taken:
            field_errors.append("Username already exists.")

    if field_errors:
        return _redirect_with_username_field_errors(
            {"username": field_errors},
            values,
        )

    user.username = username
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _redirect_with_username_field_errors(
            {"username": ["Username already exists."]},
            values,
        )
    except SQLAlchemyError:
        db.session.rollback()
        flash(
            "There was an error submitting this request. Please try again.",
            "error",
        )
        return _redirect_to_profile()

    session.pop("profile_csrf_token", None)
    flash("Username updated successfully.", "success")
    return _redirect_to_profile()


@profile_bp.route("/<int:user_id>/update-email", methods=["POST"])
@login_required
def update_email(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user != current_user:
        abort(403)

    email = (request.form.get("email") or "").strip().lower()
    values = {"email": request.form.get("email", "")}

    if not _has_valid_profile_csrf_token():
        flash("Your form has expired. Please try again.", "warning")
        return _redirect_to_profile()

    field_errors = collect_email_errors(email)
    if not field_errors:
        email_taken = db.session.scalar(
            db.select(User.id).where(
                func.lower(User.email) == email,
                User.id != user.id,
            )
        )
        if email_taken:
            field_errors.append("Email already exists.")

    if field_errors:
        return _redirect_with_email_field_errors(
            {"email": field_errors},
            values,
        )

    email_changed = user.email.lower() != email
    user.email = email
    if email_changed:
        user.email_verified = False
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _redirect_with_email_field_errors(
            {"email": ["Email already exists."]},
            values,
        )
    except SQLAlchemyError:
        db.session.rollback()
        flash(
            "There was an error submitting this request. Please try again.",
            "error",
        )
        return _redirect_to_profile()

    session.pop("profile_csrf_token", None)
    flash("Email updated successfully.", "success")
    if email_changed:
        try:
            send_verification_email(user)
        except (OSError, smtplib.SMTPException):
            current_app.logger.exception("Failed to send verification email")
            flash(
                "We could not send the verification email. Please try again later.",
                "warning",
            )
        else:
            flash("Please check your email for a verification link.", "info")
    return _redirect_to_profile()
