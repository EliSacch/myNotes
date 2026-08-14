import os

from flask import Flask, flash, redirect, request, url_for, render_template, jsonify
from flask_limiter.errors import RateLimitExceeded
from app.models import Dashboard
from sqlalchemy import text

from flask_login import login_required, current_user

from app.extensions import db, migrate, login_manager, limiter


def create_app():
    app = Flask(
        __name__,
        template_folder="./templates",
        static_folder="../static",
        
    )
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    migrate.init_app(app, db)
    limiter.init_app(app)

    from app import models  # noqa: F401
    from app.routes import auth_bp, dashboards_bp, notes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboards_bp)
    app.register_blueprint(notes_bp)

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit_exceeded(error):
        flash("Too many attempts. Please wait a moment and try again.", "warning")
        return redirect(request.referrer or url_for("auth.login"))
    
    @app.errorhandler(404)
    def handle_page_not_found(error):
        return render_template('404.html'), 404

    @app.route("/health/db")
    def handle_health_db_check():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"db_status": "ok"}), 200
        except Exception as e:
            return jsonify({"db_status": "error", "detail": str(e)}), 500
    
    @app.route("/")
    @login_required
    def index():
        from app.routes.dashboards import _dashboard_view_context

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
        return render_template("index.html", **_dashboard_view_context(default_dashboard))

    return app
