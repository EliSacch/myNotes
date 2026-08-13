import hmac
import secrets

from flask import Blueprint, abort, flash, jsonify, redirect, request, session, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Dashboard

dashboards_bp = Blueprint("dashboards", __name__, url_prefix="/dashboards")
_DASHBOARD_FORM_ERRORS_KEY = "dashboard_form_errors"
_DASHBOARD_FORM_VALUES_KEY = "dashboard_form_values"


def _dashboards_csrf_token():
    csrf_token = session.get("dashboards_csrf_token")
    if not csrf_token:
        csrf_token = secrets.token_urlsafe(32)
        session["dashboards_csrf_token"] = csrf_token
    return csrf_token


def _has_valid_dashboards_csrf_token():
    submitted_token = request.form.get("csrf_token", "")
    stored_token = session.get("dashboards_csrf_token", "")
    return (
        isinstance(submitted_token, str)
        and isinstance(stored_token, str)
        and hmac.compare_digest(submitted_token, stored_token)
    )


def _redirect_to_index_with_errors(form_key, errors, values=None):
    form_key = str(form_key)
    session[_DASHBOARD_FORM_ERRORS_KEY] = {form_key: errors}
    if values is not None:
        session[_DASHBOARD_FORM_VALUES_KEY] = {form_key: values}
    return redirect(url_for("index.index"))


def _submitted_dashboard_values():
    return {
        "name": request.form.get("name", ""),
    }

@dashboards_bp.route("/<int:dashboard_id>/<slug>")
@login_required
def get_dashboard(dashboard_id, slug):
    dashboard = db.session.get(Dashboard, dashboard_id)
    if not dashboard or dashboard.owner_id != current_user.id:
        abort(404)
    return jsonify(dashboard.to_dict())

@dashboards_bp.route("/list")
@login_required
def list_dashboards():
    dashboards = db.session.scalars(
        db.select(Dashboard)
        .where(Dashboard.owner_id == current_user.id)
        .order_by(Dashboard.created_at.asc())
    )
    return jsonify([dashboard.to_dict() for dashboard in dashboards])


@dashboards_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        errors = []
        name = (request.form.get("name") or "").strip()

        if not _has_valid_dashboards_csrf_token():
            errors.append("Invalid form submission.")
        if not name:
            errors.append("Name is required.")
        elif len(name) > 50:
            errors.append("Name must be less than 50 characters.")
        if errors:
            return _redirect_to_index_with_errors(
                "create",
                errors,
                _submitted_dashboard_values(),
            )

        new_dashboard = Dashboard(
            name=name,
            owner_id=current_user.id,
            is_default=False,
        )
        db.session.add(new_dashboard)
        try:
            db.session.commit()
            session.pop("dashboards_csrf_token", None)
        except SQLAlchemyError:
            db.session.rollback()
            return _redirect_to_index_with_errors(
                "create",
                ["There was an error submitting this request. Please try again."],
                _submitted_dashboard_values(),
            )
        return redirect(url_for("index.index"))
    return redirect(url_for("index.index"))


@dashboards_bp.route("/delete/<int:dashboard_id>", methods=["GET", "POST"])
@login_required
def delete_dashboard(dashboard_id):
    dashboard = db.session.get(Dashboard, dashboard_id)
    if not dashboard or dashboard.owner_id != current_user.id:
        flash("You are not authorized to delete this dashboard.", "error")
        return redirect(url_for("index.index"))
    if dashboard.is_default:
        flash("The default dashboard cannot be deleted.", "error")
        return redirect(url_for("index.index"))
    if request.method == "POST":
        if not _has_valid_dashboards_csrf_token():
            flash("Invalid form submission.", "error")
            return redirect(url_for("index.index"))

        db.session.delete(dashboard)
        try:
            db.session.commit()
            session.pop("dashboards_csrf_token", None)
        except SQLAlchemyError:
            db.session.rollback()
            flash("There was an error submitting this request. Please try again.", "error")
            return redirect(url_for("index.index"))
        return redirect(url_for("index.index"))
    return redirect(url_for("index.index"))
