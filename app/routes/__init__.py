from flask import Blueprint, jsonify, render_template, session
from flask_login import login_required, current_user
from sqlalchemy import text

from app.extensions import db
from app.models import Dashboard, Note

health_bp = Blueprint("health", __name__)
index_bp = Blueprint("index", __name__)

@health_bp.route("/health/db")
def health_db_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"db_status": "ok"}), 200
    except Exception as e:
        return jsonify({"db_status": "error", "detail": str(e)}), 500

@index_bp.route("/")
@login_required
def index():
    from app.routes.notes import (
        _NOTE_FORM_ERRORS_KEY,
        _NOTE_FORM_VALUES_KEY,
        _notes_csrf_token,
    )

    dashboards = list(
        db.session.scalars(
            db.select(Dashboard)
            .where(Dashboard.owner_id == current_user.id)
            .order_by(Dashboard.created_at.asc())
        )
    )

    default_dashboard = next(
        (dashboard for dashboard in dashboards if dashboard.is_default),
        None,
    )
    if default_dashboard is None:
        notes = []
    else:
        notes = list(
            db.session.scalars(
                db.select(Note)
                .where(Note.dashboard_id == default_dashboard.id)
                .order_by(Note.created_at.asc())
            )
        )

    return render_template(
        "index.html",
        page_title="Home",
        dashboards=[dashboard.to_dict() for dashboard in dashboards],
        dashboard=default_dashboard.to_dict() if default_dashboard else None,
        notes=[note.to_dict() for note in notes],
        csrf_token=_notes_csrf_token(),
        errors=session.pop(_NOTE_FORM_ERRORS_KEY, {}),
        form_values=session.pop(_NOTE_FORM_VALUES_KEY, {}),
    )

from app.routes.auth import auth_bp
from app.routes.dashboards import dashboards_bp
from app.routes.notes import notes_bp

__all__ = ["health_bp", "auth_bp", "index_bp", "dashboards_bp", "notes_bp"]
