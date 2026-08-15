from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required
from sqlalchemy import text

from app.extensions import db
from app.models import Dashboard
from app.routes.dashboards import dashboard_view_context

main_bp = Blueprint("main", __name__)


@main_bp.route("/health/db")
def handle_health_db_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"db_status": "ok"}), 200
    except Exception as e:
        return jsonify({"db_status": "error", "detail": str(e)}), 500


@main_bp.route("/")
@login_required
def index():
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
    return render_template("index.html", **dashboard_view_context(default_dashboard))
